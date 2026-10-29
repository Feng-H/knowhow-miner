"""
Adaptive Hybrid Router (Two-Tier Cognitive Cache & Drill-down)
==============================================================
Author: Huang Feng & Hermes Agent
License: CC BY-NC-SA 4.0

Implements the user-calibrated architecture:
  - Initial phase: full-text mining to distill know-how into L1 crystals.
  - Steady state: queries hit the L1 KnowledgeStore first (milliseconds,
    zero full-text cost).
  - Only when L1 confidence is low (< threshold) does the router trigger
    the L2 deep engine (FTS5 + thread-tree assembly + evidence arbitration).
  - Successful L2 dives are consolidated back into L1 (cognitive evolution),
    so the system gets faster and smarter over time while raw archives grow.

This prevents the system from slowing down as the email corpus grows.
"""

import re
from typing import List, Dict, Any, Optional

from miner.knowledge_store import KnowledgeStore
from miner.fulltext_engine import FullTextEngine
from miner.deep_retriever import DeepRetriever
from miner.codebook import FPDCodebook

DEFAULT_CONFIDENCE_THRESHOLD = 0.80


class HybridRouter:
    """
    Adaptive query router between the L1 knowledge crystal cache and the
    L2 full-text deep drill-down engine.
    """

    def __init__(self, index_db_path: str, store_db_path: str = "data/knowledge_store.db",
                 confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD):
        self.store = KnowledgeStore(store_db_path)
        self.fulltext = FullTextEngine(index_db_path)
        self.deep = DeepRetriever(index_db_path)
        self.codebook = FPDCodebook
        self.confidence_threshold = confidence_threshold

    # ------------------------------------------------------------------
    # Stage 1: Plant-model entity extraction from the user's query
    # ------------------------------------------------------------------
    def extract_plant_fingerprint(self, query: str) -> Dict[str, Any]:
        """
        Extracts industrial fingerprint entities (defect codes, equipment IDs,
        5-digit stations, layer names) from natural language using codebook.
        """
        fp: Dict[str, Any] = {
            "defect_codes": [],
            "equipment_ids": [],
            "stations": [],
            "layers": [],
            "keywords": [],
        }

        # Defect codes (AZ99, STR02X, PHT01, ILS04, SPT01...)
        for code in self.codebook.DEFECT_CATALOG:
            if re.search(rf"\b{re.escape(code)}\b", query):
                fp["defect_codes"].append(code)

        # Equipment IDs (A1PHT200, A1AOI300...) - match against known prefixes
        known_prefixes = sorted({eq[:5] for eq in getattr(self.codebook, "MACHINE_CATALOG", {})},
                                reverse=True) or ["A1PHT", "A1AOI", "A1CVD", "A1DET", "A1STR", "A1CDC"]
        for prefix in known_prefixes:
            if re.search(rf"\b{re.escape(prefix)}\d+\b", query):
                fp["equipment_ids"].append(prefix)

        # 5-digit station codes (17300, 17500, 43103...)
        fp["stations"] = list(set(re.findall(r"\b(\d{5})\b", query)))

        # Layer keywords
        layer_map = {"M2": "M2", "M1": "M1", "ITO2": "ITO2", "ITO": "ITO",
                     "PLN": "PLN", "GI": "GI", "PV": "PV", "ILD": "ILD"}
        for k, v in layer_map.items():
            if re.search(rf"\b{re.escape(k)}\b", query):
                fp["layers"].append(v)

        # Chinese symptom keywords for fallback retrieval
        symptom_kw = re.findall(r"[\u4e00-\u9fff]{2,6}", query)
        fp["keywords"] = symptom_kw[:8]
        return fp

    # ------------------------------------------------------------------
    # Stage 2: L1 crystal match with confidence scoring
    # ------------------------------------------------------------------
    def _match_l1(self, fingerprint: Dict[str, Any]) -> Dict[str, Any]:
        candidates: List[Dict[str, Any]] = []
        for code in fingerprint["defect_codes"] or [None]:
            for layer in fingerprint["layers"] or [None]:
                rows = self.store.lookup(
                    layer=layer,
                    station=fingerprint["stations"][0] if fingerprint["stations"] else None,
                    equipment=fingerprint["equipment_ids"][0] if fingerprint["equipment_ids"] else None,
                    defect_code=code,
                )
                candidates.extend(rows)

        # Deduplicate by incident_id, keep the best confidence
        best: Dict[str, Dict[str, Any]] = {}
        for c in candidates:
            iid = c["incident_id"]
            if iid not in best or c["confidence"] > best[iid]["confidence"]:
                best[iid] = c
        ranked = sorted(best.values(), key=lambda c: c["confidence"], reverse=True)

        # Confidence of the top answer: crystal confidence boosted slightly by
        # fingerprint specificity (more matched entities = higher certainty).
        specificity = sum([
            bool(fingerprint["defect_codes"]),
            bool(fingerprint["layers"]),
            bool(fingerprint["stations"] or fingerprint["equipment_ids"]),
        ])
        top_confidence = 0.0
        if ranked:
            top_confidence = min(1.0, ranked[0]["confidence"] + 0.05 * specificity)

        return {"confidence": top_confidence, "matches": ranked[:5]}

    # ------------------------------------------------------------------
    # Stage 3: L2 deep drill-down (only when confidence is insufficient)
    # ------------------------------------------------------------------
    def _deep_dive(self, query: str, fingerprint: Dict[str, Any]) -> Dict[str, Any]:
        terms = (
            fingerprint["defect_codes"]
            + fingerprint["equipment_ids"]
            + fingerprint["stations"]
            + fingerprint["layers"]
            + fingerprint["keywords"]
        )
        if not terms:
            terms = query.split()[:8]

        hits = self.fulltext.search(terms, limit=30)
        seed_ids = [h["message_id"] for h in hits if h.get("message_id")]
        threads = self.deep.assemble_threads(seed_ids)
        attachments = self.deep.extract_attachment_evidence(threads)

        threads_view = [
            {
                "thread_key": t["thread_key"],
                "message_count": t["message_count"],
                "messages": [
                    {"message_id": m.get("message_id"), "date": m.get("date_str"),
                     "from": m.get("from_addr"), "subject": m.get("subject")}
                    for m in t["messages"][:15]
                ]
            }
            for t in threads
        ]
        return {
            "hits": hits[:10],
            "threads": threads_view,
            "attachment_evidence": attachments[:15],
            "scanned_emails": len(hits),
        }

    # ------------------------------------------------------------------
    # Stage 4: Cognitive evolution — consolidate dive results into L1
    # ------------------------------------------------------------------
    def _consolidate_to_l1(self, query: str, fingerprint: Dict[str, Any],
                           dive_result: Dict[str, Any]) -> Optional[str]:
        """
        Pack a successful deep dive into a new L1 crystal so future queries
        of the same fingerprint never need to dive again.
        """
        threads = dive_result.get("threads", [])
        if not threads:
            return None

        # Pick the most authoritative/terminal message of the largest thread
        # as the provisional conclusion carrier (real deployment: LLM quintet
        # extraction + Grade A~E arbitration run here).
        largest = max(threads, key=lambda t: t["message_count"])
        if not largest.get("messages"):
            return None
        final_msg = largest["messages"][-1]

        fingerprint_str = "|".join(
            (fingerprint["layers"][:1] or [""])
            + (fingerprint["stations"][:1] or [""])
            + (fingerprint["equipment_ids"][:1] or [""])
            + (fingerprint["defect_codes"][:1] or [""])
        )

        incident_id = f"dive_{abs(hash(query)) % (10**10)}"
        self.store.upsert_crystal({
            "incident_id": incident_id,
            "plant_fingerprint": fingerprint_str,
            "layer": fingerprint["layers"][0] if fingerprint["layers"] else None,
            "station": fingerprint["stations"][0] if fingerprint["stations"] else None,
            "equipment": fingerprint["equipment_ids"][0] if fingerprint["equipment_ids"] else None,
            "defect_code": fingerprint["defect_codes"][0] if fingerprint["defect_codes"] else None,
            "symptom": query[:200],
            "ground_truth_mechanism": None,   # filled by causal extractor in full pipeline
            "pca_action": None,
            "dfm_rule": None,
            "evidence_grade": "E",
            "evidence_anchor": [
                {"message_id": final_msg.get("message_id"),
                 "subject": final_msg.get("subject"),
                 "date": final_msg.get("date")}
            ],
            "confidence": 0.55,   # provisional; rises after human/LLM confirmation
        })
        return incident_id

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------
    def answer(self, query: str) -> Dict[str, Any]:
        """
        Answers an industrial troubleshooting query using the two-tier policy.
        """
        fingerprint = self.extract_plant_fingerprint(query)
        l1 = self._match_l1(fingerprint)

        if l1["confidence"] >= self.confidence_threshold:
            top = l1["matches"][0]
            self.store.record_hit(top["incident_id"])
            return {
                "query": query,
                "route": "L1_CACHE_HIT",
                "confidence": round(l1["confidence"], 3),
                "fingerprint": fingerprint,
                "answer": {
                    "incident_id": top["incident_id"],
                    "symptom": top["symptom"],
                    "ground_truth_mechanism": top["ground_truth_mechanism"],
                    "pca_action": top["pca_action"],
                    "dfm_rule": top["dfm_rule"],
                    "evidence_grade": top["evidence_grade"],
                    "evidence_anchor": top["evidence_anchor"],
                },
                "l1_matches": len(l1["matches"]),
            }

        # Low confidence: deep dive into L2
        dive = self._deep_dive(query, fingerprint)
        new_id = self._consolidate_to_l1(query, fingerprint, dive)
        return {
            "query": query,
            "route": "L2_DEEP_DIVE",
            "confidence": round(l1["confidence"], 3),
            "fingerprint": fingerprint,
            "dive": dive,
            "consolidated_crystal": new_id,
        }
