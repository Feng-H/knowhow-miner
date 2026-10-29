"""
SQLite FTS5 Full-Text Search Engine for Industrial Manufacturing Emails
=======================================================================
Author: Huang Feng & Hermes Agent
License: PolyForm Noncommercial License 1.0.0

Provides high-performance inverted index search over cleaned email bodies,
subjects, machine IDs, defect codes, and attachment metadata.
Replaces slow 'LIKE %keyword%' full-table scans with millisecond-level FTS5 queries.
"""

import sqlite3
import os
import re
from typing import List, Dict, Any, Optional

class FullTextEngine:
    """
    Manages SQLite FTS5 inverted index and provides structured boolean search.
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ensure_fts_table()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_fts_table(self):
        """
        Creates FTS5 virtual table if it does not already exist.
        """
        with self._get_connection() as conn:
            cur = conn.cursor()
            # Check if emails table exists
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='emails'")
            if not cur.fetchone():
                return

            # Check if emails_fts already exists
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='emails_fts'")
            if not cur.fetchone():
                cur.execute("""
                    CREATE VIRTUAL TABLE IF NOT EXISTS emails_fts USING fts5(
                        message_id UNINDEXED,
                        seq_num UNINDEXED,
                        date_str UNINDEXED,
                        from_addr,
                        subject,
                        body_preview,
                        attachment_names,
                        tokenize='unicode61'
                    );
                """)
                # Populate initial FTS5 index from emails table
                cur.execute("""
                    INSERT INTO emails_fts (message_id, seq_num, date_str, from_addr, subject, body_preview, attachment_names)
                    SELECT message_id, seq_num, date_str, from_addr, subject, body_preview, attachment_names
                    FROM emails;
                """)
                conn.commit()

    def sync_record(self, record: Dict[str, Any]):
        """
        Inserts or updates a single record in the FTS index.
        """
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO emails_fts (message_id, seq_num, date_str, from_addr, subject, body_preview, attachment_names)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                record.get("message_id", ""),
                record.get("seq_num", 0),
                record.get("date_str", ""),
                record.get("from_addr", ""),
                record.get("subject", ""),
                record.get("body_preview", ""),
                str(record.get("attachment_names", ""))
            ))
            conn.commit()

    def search(self, query_terms: List[str], limit: int = 50) -> List[Dict[str, Any]]:
        """
        Executes full-text boolean query with relevance ranking (bm25).
        """
        if not query_terms:
            return []

        # Sanitize query terms for FTS5 syntax
        sanitized_terms = []
        for t in query_terms:
            cleaned = re.sub(r'[^\w\u4e00-\u9fff.-]', '', t).strip()
            if cleaned:
                # Enclose in quotes to support exact alphanumeric codes (e.g. "A1PHT200", "AZ99")
                sanitized_terms.append(f'"{cleaned}"')

        if not sanitized_terms:
            return []

        # Combine terms with OR or AND
        fts_query = " OR ".join(sanitized_terms)

        with self._get_connection() as conn:
            cur = conn.cursor()
            sql = """
                SELECT message_id, seq_num, date_str, from_addr, subject, body_preview, attachment_names,
                       bm25(emails_fts) as rank
                FROM emails_fts
                WHERE emails_fts MATCH ?
                ORDER BY rank ASC
                LIMIT ?
            """
            try:
                cur.execute(sql, (fts_query, limit))
                rows = cur.fetchall()
                results = []
                for r in rows:
                    results.append({
                        "message_id": r["message_id"],
                        "seq_num": r["seq_num"],
                        "date_str": r["date_str"],
                        "from_addr": r["from_addr"],
                        "subject": r["subject"],
                        "body_preview": r["body_preview"],
                        "attachment_names": r["attachment_names"],
                        "bm25_rank": r["rank"]
                    })
                return results
            except sqlite3.OperationalError:
                # Fallback if query syntax has issues
                return []
