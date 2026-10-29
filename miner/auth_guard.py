"""
KnowhowCraft MCP Authentication, Rate Limiting & Concurrency Guard
==================================================================
Author: John Huang & Hermes Agent
License: CC BY-NC-SA 4.0 (Creative Commons Attribution-NonCommercial-ShareAlike 4.0)

Handles:
  1. API Token Verification (Bearer token via Authorization header or query string)
  2. Multi-tier Permission Control (trial, commercial, enterprise)
  3. Sliding-Window Rate Limiting (anti-scraping / DDoS protection)
  4. Active Concurrency Tracking per Token
  5. Anti-Theft Protection for Public Web Queries (/api/diagnose)
     - Origin/Referer anti-leech verification
     - IP sliding-window throttling (5 rpm for custom text queries)
     - Honey-pot scanner detection & cooldown
     - Quantitative parameter redaction for unauthenticated web visitors
  6. Audit Logging & Call Metrics
"""

import os
import time
import sqlite3
import secrets
import threading
from urllib.parse import urlparse
from typing import Optional, Tuple, Dict, Any, List

AUTH_DB_PATH = os.environ.get("AUTH_DB_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "tokens.db"))

_concurrency_lock = threading.Lock()
_active_concurrency: Dict[str, int] = {}

_rate_limit_lock = threading.Lock()
_call_history: Dict[str, List[float]] = {}  # token_or_ip -> list of timestamps
_scanner_misses: Dict[str, List[float]] = {}  # ip -> list of timestamps
_banned_until: Dict[str, float] = {}  # ip -> ban_timestamp

# Allowed domains for web interface queries
ALLOWED_HOSTS = {
    "fpd.knowhowcraft.com",
    "knowhowcraft.com",
    "localhost",
    "127.0.0.1"
}

def init_auth_db():
    os.makedirs(os.path.dirname(AUTH_DB_PATH) or ".", exist_ok=True)
    with sqlite3.connect(AUTH_DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS api_tokens (
                token_id INTEGER PRIMARY KEY AUTOINCREMENT,
                token_key TEXT UNIQUE NOT NULL,
                client_name TEXT NOT NULL,
                tier TEXT NOT NULL DEFAULT 'trial',
                rate_limit_per_min INTEGER NOT NULL DEFAULT 10,
                max_concurrency INTEGER NOT NULL DEFAULT 2,
                expires_at REAL,
                is_active INTEGER NOT NULL DEFAULT 1,
                total_calls INTEGER NOT NULL DEFAULT 0,
                last_call_at REAL,
                created_at REAL NOT NULL
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_token_key ON api_tokens(token_key)")
        conn.commit()

class TokenContext:
    def __init__(self, token_key: str, client_name: str, tier: str, rate_limit_per_min: int, max_concurrency: int, expires_at: Optional[float]):
        self.token_key = token_key
        self.client_name = client_name
        self.tier = tier
        self.rate_limit_per_min = rate_limit_per_min
        self.max_concurrency = max_concurrency
        self.expires_at = expires_at

    def __enter__(self):
        with _concurrency_lock:
            current = _active_concurrency.get(self.token_key, 0)
            if current >= self.max_concurrency:
                raise ConcurrencyLimitExceeded(f"并发超出许可限制（当前允许最大并发: {self.max_concurrency}）")
            _active_concurrency[self.token_key] = current + 1
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        with _concurrency_lock:
            current = _active_concurrency.get(self.token_key, 1)
            if current <= 1:
                _active_concurrency.pop(self.token_key, None)
            else:
                _active_concurrency[self.token_key] = current - 1

class ConcurrencyLimitExceeded(Exception):
    pass

class RateLimitExceeded(Exception):
    pass

class AuthenticationFailed(Exception):
    pass

def generate_token(client_name: str, tier: str = "commercial", days: int = 365, rate_limit_per_min: int = 60, max_concurrency: int = 5) -> str:
    init_auth_db()
    token_key = f"khc_{tier[:4]}_{secrets.token_hex(16)}"
    now = time.time()
    expires_at = now + (days * 86400) if days > 0 else None
    
    with sqlite3.connect(AUTH_DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO api_tokens (token_key, client_name, tier, rate_limit_per_min, max_concurrency, expires_at, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, 1, ?)
        """, (token_key, client_name, tier, rate_limit_per_min, max_concurrency, expires_at, now))
        conn.commit()
    return token_key

def verify_and_acquire(auth_header: Optional[str], query_token: Optional[str], client_ip: str) -> TokenContext:
    """
    Validates token, enforces rate limiting, and returns a TokenContext.
    If no token is supplied, falls back to a strictly throttled public-trial quota.
    """
    init_auth_db()
    raw_token = None
    if auth_header:
        parts = auth_header.strip().split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            raw_token = parts[1]
        elif len(parts) == 1:
            raw_token = parts[0]
            
    if not raw_token and query_token:
        raw_token = query_token.strip()

    now = time.time()

    # Public Trial Fallback (No token provided)
    if not raw_token:
        trial_id = f"ip_{client_ip}"
        _check_rate_limit(trial_id, limit_per_min=10, now=now)
        return TokenContext(
            token_key=trial_id,
            client_name="匿名公共试用",
            tier="trial",
            rate_limit_per_min=10,
            max_concurrency=2,
            expires_at=None
        )

    # Commercial / Enterprise Token Lookup
    with sqlite3.connect(AUTH_DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM api_tokens WHERE token_key = ?", (raw_token,))
        row = cur.fetchone()

        if not row:
            raise AuthenticationFailed("无效的授权凭证 (Invalid Token Key)")

        if not row["is_active"]:
            raise AuthenticationFailed("该授权凭证已被吊销或停用 (Token Revoked)")

        if row["expires_at"] and now > row["expires_at"]:
            raise AuthenticationFailed("授权凭证已过期，请联系续费 (Token Expired)")

        # Record call metric
        cur.execute("UPDATE api_tokens SET total_calls = total_calls + 1, last_call_at = ? WHERE token_id = ?", (now, row["token_id"]))
        conn.commit()

        _check_rate_limit(raw_token, limit_per_min=row["rate_limit_per_min"], now=now)

        return TokenContext(
            token_key=raw_token,
            client_name=row["client_name"],
            tier=row["tier"],
            rate_limit_per_min=row["rate_limit_per_min"],
            max_concurrency=row["max_concurrency"],
            expires_at=row["expires_at"]
        )

def _check_rate_limit(key: str, limit_per_min: int, now: float):
    window_start = now - 60.0
    with _rate_limit_lock:
        calls = _call_history.get(key, [])
        calls = [t for t in calls if t > window_start]
        if len(calls) >= limit_per_min:
            raise RateLimitExceeded(f"访问频率超出配额（限制每分钟最多 {limit_per_min} 次，防爬虫机制已触发）")
        calls.append(now)
        _call_history[key] = calls

# ==============================================================================
# Public Web Anti-Scraping & Anti-Theft Guard (/api/diagnose)
# ==============================================================================

def validate_web_origin(origin: Optional[str], referer: Optional[str]) -> bool:
    """
    Prevents unauthorized third-party websites from embedding or hotlinking our API.
    Direct browser requests (without Origin/Referer in some browsers) are permitted,
    but explicit foreign cross-origin domains are strictly blocked.
    """
    check_url = origin or referer
    if not check_url:
        return True
    try:
        parsed = urlparse(check_url)
        host = (parsed.hostname or "").lower()
        if not host:
            return True
        for allowed in ALLOWED_HOSTS:
            if host == allowed or host.endswith("." + allowed):
                return True
        return False
    except Exception:
        return False

def check_web_query_rate_limit(client_ip: str, is_preset: bool = False) -> Tuple[bool, str]:
    """
    Protects /api/diagnose against automated dictionary brute-forcing.
    - Presets: max 15 requests / min (accommodating rapid chip clicking by humans)
    - Custom text search: max 5 requests / min
    - Honey-pot scanner detection: 4 consecutive misses in 15s triggers 120s ban.
    """
    now = time.time()
    with _rate_limit_lock:
        # 1. Check if IP is currently under scanner cooldown
        banned_until = _banned_until.get(client_ip, 0)
        if now < banned_until:
            rem = int(banned_until - now)
            return False, f"⚠️ 检测到高频异常扫描行为，IP 已被临时冷却防护（剩余 {rem} 秒）。请使用正常浏览器体验或联系商业授权。"

        # 2. Check sliding window
        limit = 15 if is_preset else 5
        key = f"web_{client_ip}"
        calls = _call_history.get(key, [])
        calls = [t for t in calls if t > (now - 60.0)]
        if len(calls) >= limit:
            return False, f"⚠️ 访问过于频繁（公共试用每分钟限 {limit} 次，防爬虫风控已触发）。批量调取请申请商业 MCP Token。"
        calls.append(now)
        _call_history[key] = calls
        return True, ""

def record_scanner_miss(client_ip: str):
    """
    Called when an unknown query returns a miss.
    If 4 misses happen within 15s, IP is banned for 120s to halt dictionary scanners.
    """
    now = time.time()
    with _rate_limit_lock:
        misses = _scanner_misses.get(client_ip, [])
        misses = [t for t in misses if t > (now - 15.0)]
        misses.append(now)
        _scanner_misses[client_ip] = misses
        if len(misses) >= 4:
            _banned_until[client_ip] = now + 120.0

def redact_for_public_web(diag: dict) -> dict:
    """
    Data Tiering: Public web visitors receive qualitative physical mechanisms and symptoms,
    but exact production numerical formulas and critical offsets are protected.
    """
    if not diag:
        return diag
    result = dict(diag)
    dfm = result.get("dfm_rule")
    if dfm and isinstance(dfm, dict):
        redacted_dfm = dict(dfm)
        redacted_dfm["formula"] = "🔒 [量产级物理公差计算参数已保护，商业 Token / MCP 专享]"
        redacted_dfm["is_locked"] = True
        result["dfm_rule"] = redacted_dfm
    return result
