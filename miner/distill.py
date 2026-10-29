"""
Know-how Distillation: Gold Standard / Pipeline output -> L1 Crystals
=====================================================================
Author: Huang Feng & Hermes Agent
License: CC BY-NC-SA 4.0

Implements the "initial full-corpus mining" phase of the user-calibrated
architecture: converged causal quintets (validated by Levels 3/4/5) are
distilled into the L1 KnowledgeStore as high-confidence crystals, so that
daily queries hit the cache and never re-scan the full archive.
"""

import json
import os
from typing import Dict, Any, List

from miner.knowledge_store import KnowledgeStore

# Confidence granted per evidence grade when crystallizing a converged incident.
GRADE_CONFIDENCE = {
    "A": 0.95,
    "B": 0.85,
    "C": 0.75,
    "D": 0.60,
    "E": 0.50,
}


def distill_gold_standard(gold_path: str, store_db_path: str = "data/knowledge_store.db") -> Dict[str, Any]:
    """
    Seeds the L1 store from a validated gold-standard / extracted-incidents JSON.
    Each incident becomes one crystal with evidence-graded confidence.
    """
    with open(gold_path, "r", encoding="utf-8") as f:
        gold = json.load(f)

    store = KnowledgeStore(store_db_path)
    created = 0

    for inc in gold.get("incidents", []):
        meta = inc.get("meta", {})
        symptom = inc.get("symptom", {})
        gt = inc.get("ground_truth_physics", {})
        pca = inc.get("pca_solution", {})
        dfm = inc.get("dfm_rule", {})
        dec = inc.get("pr_vs_physics_decoupling", {})

        # Derive the evidence anchor from validation probe + mechanism (traceable)
        evidence_anchor = [{
            "incident_id": inc.get("id"),
            "quote": gt.get("mechanism", "")[:200],
            "probe": inc.get("validation_probe", {}).get("method", ""),
        }]

        layer = meta.get("layer", "")
        station = meta.get("station", "")
        defect_code = symptom.get("defect_code", "")

        fingerprint = "|".join([layer, station, defect_code])

        store.upsert_crystal({
            "incident_id": inc.get("id"),
            "plant_fingerprint": fingerprint,
            "layer": _norm_layer(layer),
            "station": station,
            "equipment": meta.get("equipment"),
            "defect_code": defect_code,
            "symptom": symptom.get("description", "")[:300],
            "ground_truth_mechanism": gt.get("mechanism"),
            "pca_action": pca.get("action"),
            "dfm_rule": dfm,
            "evidence_grade": "A" if gt.get("mechanism") and pca.get("action") else "B",
            "evidence_anchor": evidence_anchor,
            "confidence": GRADE_CONFIDENCE["A"] if (gt.get("mechanism") and pca.get("action")) else GRADE_CONFIDENCE["B"],
        })
        created += 1

    return {"distilled_incidents": created, "store_stats": store.stats()}


def _norm_layer(layer: str) -> str:
    """Normalize layer names like 'M2_SourceDrain' -> 'M2' for fingerprint lookup."""
    return layer.split("_")[0] if layer else layer


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Distill validated incidents into L1 knowledge crystals")
    parser.add_argument("--gold", default="benchmarks/gold_standard_v1.json")
    parser.add_argument("--store", default="data/knowledge_store.db")
    args = parser.parse_args()
    result = distill_gold_standard(args.gold, args.store)
    print(json.dumps(result, ensure_ascii=False, indent=2))
