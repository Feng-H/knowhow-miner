"""
Deep Retriever: Thread-tree Assembly & Multi-Modal Evidence Unpacking
=====================================================================
Author: Huang Feng & Hermes Agent
License: PolyForm Noncommercial License 1.0.0

Given a set of seed message IDs from full-text search, this module:
  1. Reconstructs the full email conversation tree (Message-ID / In-Reply-To);
  2. Extracts attachment evidence (Excel split tables, PPT 5-Why reports);
  3. Feeds assembled evidence into the 5-grade arbitration engine.
"""

import sqlite3
import re
from typing import List, Dict, Any, Optional
from collections import defaultdict

class DeepRetriever:
    """
    L2 Deep Drill-down Engine: reconstructs conversation trees and
    gathers multi-modal evidence from raw email archives.
    """

    def __init__(self, db_path: str):
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def assemble_threads(self, seed_message_ids: List[str], max_depth: int = 10) -> List[Dict[str, Any]]:
        """
        Reconstructs complete email threads from seed messages by walking
        Message-ID / In-Reply-To chains bidirectionally. Falls back to
        subject-prefix grouping ("答复: ...") when In-Reply-To headers are absent.
        """
        if not seed_message_ids:
            return []

        seeds = list(seed_message_ids)
        visited = set()
        threads = defaultdict(list)

        with self._get_connection() as conn:
            cur = conn.cursor()

            # Detect whether in_reply_to threading is available
            cur.execute("PRAGMA table_info(emails)")
            columns = {r[1] for r in cur.fetchall()}
            has_reply_to = "in_reply_to" in columns

            def _walk(msg_id: str, thread_key: str, depth: int):
                if depth > max_depth or msg_id in visited or not msg_id:
                    return
                visited.add(msg_id)

                cur.execute(
                    "SELECT * FROM emails WHERE message_id = ?", (msg_id,)
                )
                row = cur.fetchone()
                if not row:
                    return

                threads[thread_key].append(dict(row))

                if has_reply_to:
                    # Walk parents (In-Reply-To)
                    in_reply_to = row["in_reply_to"] if "in_reply_to" in row.keys() else None
                    if in_reply_to:
                        _walk(in_reply_to, thread_key, depth + 1)

                    # Walk children (emails replying to this one)
                    cur.execute(
                        "SELECT message_id FROM emails WHERE in_reply_to = ?", (msg_id,)
                    )
                    for child in cur.fetchall():
                        _walk(child["message_id"], thread_key, depth + 1)

            for seed in seeds:
                if seed not in visited:
                    _walk(seed, seed, 0)

        # Fallback: group by normalized subject when reply headers are missing.
        if not has_reply_to:
            subj_groups = defaultdict(dict)  # key -> {message_id: row} for dedup
            norm = lambda s: re.sub(r"^(答复|回复|Re|Fwd|FW|转发)\s*:\s*", "", str(s or ""), flags=re.IGNORECASE).strip()
            with self._get_connection() as conn:
                cur = conn.cursor()
                for seed in seeds:
                    cur.execute("SELECT * FROM emails WHERE message_id = ?", (seed,))
                    row = cur.fetchone()
                    if not row:
                        continue
                    key = norm(row["subject"])
                    cur.execute("SELECT * FROM emails")
                    for r in cur.fetchall():
                        if norm(r["subject"]) == key:
                            subj_groups[key][r["message_id"]] = dict(r)
            threads = {k: list(v.values()) for k, v in subj_groups.items()}

        # Sort each thread by date
        assembled = []
        for key, msgs in threads.items():
            msgs.sort(key=lambda m: m.get("date_str", ""))
            assembled.append({
                "thread_key": key,
                "message_count": len(msgs),
                "messages": msgs
            })
        return assembled

    def extract_attachment_evidence(self, threads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Scans assembled threads for high-value technical attachments
        (Excel split tables, PPT 5-Why reports) and extracts them.
        """
        import json

        evidence = []
        exc_patterns = [r"\.xlsx?$"]
        ppt_pattern = r"\.pptx?$"
        five_why_pattern = re.compile(r"(5[Ww]hy|五个为什么|根因|root\s*cause)", re.IGNORECASE)
        split_pattern = re.compile(r"(split|分件|实验数据|DOE)", re.IGNORECASE)

        for th in threads:
            for msg in th["messages"]:
                att_names = msg.get("attachment_names", "") or ""
                # attachment_names may be JSON-encoded list or plain string
                names = []
                if isinstance(att_names, str):
                    try:
                        parsed = json.loads(att_names)
                        names = parsed if isinstance(parsed, list) else [str(parsed)]
                    except Exception:
                        names = [att_names] if att_names else []
                elif isinstance(att_names, list):
                    names = att_names

                body_text = str(msg.get("body_preview", "") or "")
                for name in names:
                    name_str = str(name)
                    is_excel = any(re.search(p, name_str, re.IGNORECASE) for p in exc_patterns)
                    is_ppt = re.search(ppt_pattern, name_str, re.IGNORECASE)
                    evidence.append({
                        "thread_key": th["thread_key"],
                        "message_id": msg.get("message_id", ""),
                        "attachment": name_str,
                        "type": "excel_split" if is_excel else ("ppt_5why" if is_ppt else "other"),
                        "is_split_table": bool(split_pattern.search(name_str)),
                        "is_five_why": bool(five_why_pattern.search(name_str) or five_why_pattern.search(body_text))
                    })
        return evidence
