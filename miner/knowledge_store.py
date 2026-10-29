"""
L1 Distilled Know-how Store (Cognitive Cache)
=============================================
Author: Huang Feng & Hermes Agent
License: CC BY-NC-SA 4.0

A lightweight, high-density persistence layer storing converged causal
quintets, DFM rules, and their evidence anchors. Designed for millisecond
queries regardless of the size of the underlying raw email archive.

The store is intentionally small (thousands of records, a few MB) so that
daily high-frequency queries never touch the full-text archive (L2).
"""

import sqlite3
import os
import json
from typing import List, Dict, Any, Optional

SCHEMA = """
CREATE TABLE IF NOT EXISTS knowledge_crystals (
    incident_id TEXT PRIMARY KEY,
    plant_fingerprint TEXT NOT NULL,          -- e.g. "M2|17300|A1PHT200|AZ99"
    layer TEXT,                                -- e.g. M2, ITO2, PLN
    station TEXT,                              -- e.g. 17300, 17500
    equipment TEXT,                            -- e.g. A1PHT200
    defect_code TEXT,                          -- e.g. AZ99
    symptom TEXT,
    ground_truth_mechanism TEXT,               -- internal physics root cause
    pca_action TEXT,                           -- permanent corrective action
    dfm_rule TEXT,                             -- DFM red-line rule (JSON)
    evidence_grade TEXT,                       -- Grade A~E
    evidence_anchor TEXT,                      -- JSON: [{message_id, quote, date}]
    confidence REAL DEFAULT 0.5,
    hit_count INTEGER DEFAULT 0,
    created_at TEXT,
    updated_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_crystal_fingerprint ON knowledge_crystals(plant_fingerprint);
CREATE INDEX IF NOT EXISTS idx_crystal_layer ON knowledge_crystals(layer);
CREATE INDEX IF NOT EXISTS idx_crystal_defect ON knowledge_crystals(defect_code);
"""

class KnowledgeStore:
    """
    L1 crystallized knowledge store with millisecond-level lookup.
    """

    def __init__(self, db_path: str = "data/knowledge_store.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
        with self._conn() as conn:
            conn.executescript(SCHEMA)

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def upsert_crystal(self, record: Dict[str, Any]) -> bool:
        """
        Inserts or updates a distilled knowledge crystal.
        Used both by initial mining and by L2 deep-dive consolidation (cognitive evolution).
        """
        with self._conn() as conn:
            conn.execute("""
                INSERT INTO knowledge_crystals (
                    incident_id, plant_fingerprint, layer, station, equipment, defect_code,
                    symptom, ground_truth_mechanism, pca_action, dfm_rule,
                    evidence_grade, evidence_anchor, confidence, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
                ON CONFLICT(incident_id) DO UPDATE SET
                    ground_truth_mechanism=excluded.ground_truth_mechanism,
                    pca_action=excluded.pca_action,
                    dfm_rule=excluded.dfm_rule,
                    evidence_grade=excluded.evidence_grade,
                    evidence_anchor=excluded.evidence_anchor,
                    confidence=excluded.confidence,
                    updated_at=datetime('now')
            """, (
                record.get("incident_id"),
                record.get("plant_fingerprint", ""),
                record.get("layer"),
                record.get("station"),
                record.get("equipment"),
                record.get("defect_code"),
                record.get("symptom"),
                record.get("ground_truth_mechanism"),
                record.get("pca_action"),
                json.dumps(record.get("dfm_rule"), ensure_ascii=False) if record.get("dfm_rule") else None,
                record.get("evidence_grade", "E"),
                json.dumps(record.get("evidence_anchor", []), ensure_ascii=False),
                record.get("confidence", 0.5)
            ))
            return True

    def lookup(self, layer: Optional[str] = None, station: Optional[str] = None,
               equipment: Optional[str] = None, defect_code: Optional[str] = None,
               keyword: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fast L1 lookup by plant-model fingerprint components or symptom keyword.
        Returns matching crystals ordered by confidence.
        """
        conditions, params = [], []
        if layer:
            conditions.append("layer = ?"); params.append(layer)
        if station:
            conditions.append("station = ?"); params.append(station)
        if equipment:
            conditions.append("equipment = ?"); params.append(equipment)
        if defect_code:
            conditions.append("defect_code = ?"); params.append(defect_code)
        if keyword:
            conditions.append("(symptom LIKE ? OR ground_truth_mechanism LIKE ? OR pca_action LIKE ?)")
            params.extend([f"%{keyword}%"] * 3)

        sql = "SELECT * FROM knowledge_crystals"
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        sql += " ORDER BY confidence DESC, updated_at DESC LIMIT 20"

        with self._conn() as conn:
            rows = conn.execute(sql, params).fetchall()
            return [dict(r) for r in rows]

    def record_hit(self, incident_id: str):
        """Bump hit counter when a crystal is used to answer a query (popular knowledge surfaces faster)."""
        with self._conn() as conn:
            conn.execute(
                "UPDATE knowledge_crystals SET hit_count = hit_count + 1 WHERE incident_id = ?",
                (incident_id,)
            )

    def stats(self) -> Dict[str, Any]:
        with self._conn() as conn:
            total = conn.execute("SELECT COUNT(*) FROM knowledge_crystals").fetchone()[0]
            by_grade = conn.execute(
                "SELECT evidence_grade, COUNT(*) FROM knowledge_crystals GROUP BY evidence_grade"
            ).fetchall()
            avg_conf = conn.execute(
                "SELECT AVG(confidence) FROM knowledge_crystals"
            ).fetchone()[0]
            return {
                "total_crystals": total,
                "by_evidence_grade": {r[0]: r[1] for r in by_grade},
                "avg_confidence": round(avg_conf, 3) if avg_conf else 0.0
            }
