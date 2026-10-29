"""
KnowhowCraft Token Administration & License Issuer
===================================================
Author: John Huang & Hermes Agent
License: CC BY-NC-SA 4.0 (Creative Commons Attribution-NonCommercial-ShareAlike 4.0)

CLI tool to issue, list, revoke, and inspect commercial MCP authorization tokens.
"""

import sys
import os
import argparse
import time
import sqlite3

AUTH_DB_PATH = os.environ.get(
    "AUTH_DB_PATH",
    "/home/ubuntu/fpd-work/fpd-server/data/tokens.db"
)

def get_conn():
    os.makedirs(os.path.dirname(AUTH_DB_PATH) or ".", exist_ok=True)
    conn = sqlite3.connect(AUTH_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS api_tokens (
                token_id INTEGER PRIMARY KEY AUTOINCREMENT,
                token_key TEXT UNIQUE NOT NULL,
                client_name TEXT NOT NULL,
                tier TEXT NOT NULL DEFAULT 'commercial',
                rate_limit_per_min INTEGER NOT NULL DEFAULT 60,
                max_concurrency INTEGER NOT NULL DEFAULT 5,
                expires_at REAL,
                is_active INTEGER NOT NULL DEFAULT 1,
                total_calls INTEGER NOT NULL DEFAULT 0,
                last_call_at REAL,
                created_at REAL NOT NULL
            )
        """)
        conn.commit()

def cmd_create(args):
    import secrets
    init_db()
    tier_prefix = args.tier[:4]
    token_key = f"khc_{tier_prefix}_{secrets.token_hex(16)}"
    now = time.time()
    expires_at = now + (args.days * 86400) if args.days > 0 else None

    with get_conn() as conn:
        conn.execute("""
            INSERT INTO api_tokens (token_key, client_name, tier, rate_limit_per_min, max_concurrency, expires_at, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, 1, ?)
        """, (token_key, args.client, args.tier, args.rate_limit, args.concurrency, expires_at, now))
        conn.commit()

    exp_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(expires_at)) if expires_at else "永久有效"

    print("=" * 65)
    print("🎉 商业授权 Token 生成成功！")
    print("=" * 65)
    print(f"客户名称:   {args.client}")
    print(f"授权等级:   {args.tier}")
    print(f"授权 Token: {token_key}")
    print(f"到期时间:   {exp_str} ({args.days} 天)")
    print(f"并发配额:   {args.concurrency} 路并发")
    print(f"频率上限:   {args.rate_limit} 次/分钟")
    print("-" * 65)
    print("📋 交付客户的 WorkBuddy / Cursor 配置代码 (mcp.json):")
    print(f"""{{
  "mcpServers": {{
    "fpd-knowhowcraft": {{
      "url": "https://fpd.knowhowcraft.com/sse",
      "headers": {{
        "Authorization": "Bearer {token_key}"
      }}
    }}
  }}
}}""")
    print("=" * 65)

def cmd_list(args):
    init_db()
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM api_tokens ORDER BY created_at DESC")
        rows = cur.fetchall()

    if not rows:
        print("暂无已发行的授权 Token。")
        return

    print("=" * 95)
    print(f"{'ID':<4} {'客户名称':<16} {'授权级别':<10} {'状态':<6} {'总调用':<8} {'并发/限流':<12} {'到期日':<20}")
    print("-" * 95)
    now = time.time()
    for r in rows:
        status = "正常" if r["is_active"] else "已吊销"
        if r["expires_at"] and now > r["expires_at"]:
            status = "已过期"
        exp_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(r["expires_at"])) if r["expires_at"] else "永久"
        quota_str = f"{r['max_concurrency']}路 / {r['rate_limit_per_min']}rpm"
        print(f"{r['token_id']:<4} {r['client_name']:<16} {r['tier']:<10} {status:<6} {r['total_calls']:<8} {quota_str:<12} {exp_str:<20}")
        print(f"     Token: {r['token_key']}")
    print("=" * 95)

def cmd_revoke(args):
    init_db()
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE api_tokens SET is_active = 0 WHERE token_key = ? OR client_name = ? OR token_id = ?", (args.target, args.target, args.target))
        if cur.rowcount > 0:
            conn.commit()
            print(f"✓ 成功吊销授权: {args.target}")
        else:
            print(f"未找到匹配的授权 Token 或客户名称: {args.target}")

def main():
    parser = argparse.ArgumentParser(description="KnowhowCraft MCP Token Issuer")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    # create
    p_create = subparsers.add_parser("create", help="生成新的客户授权 Token")
    p_create.add_argument("--client", required=True, help="客户单位或工程师称呼（如 '上海某微电子'）")
    p_create.add_argument("--tier", choices=["trial", "commercial", "enterprise"], default="commercial", help="授权级别")
    p_create.add_argument("--days", type=int, default=365, help="有效天数（默认 365 天，0 表示永久）")
    p_create.add_argument("--concurrency", type=int, default=5, help="最大并发路数（默认 5）")
    p_create.add_argument("--rate-limit", type=int, default=60, help="每分钟最大请求数（默认 60）")
    p_create.set_defaults(func=cmd_create)

    # list
    p_list = subparsers.add_parser("list", help="查看所有授权 Token 与调用统计")
    p_list.set_defaults(func=cmd_list)

    # revoke
    p_revoke = subparsers.add_parser("revoke", help="吊销或停用某个 Token")
    p_revoke.add_argument("target", help="Token 密钥或客户名称")
    p_revoke.set_defaults(func=cmd_revoke)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
