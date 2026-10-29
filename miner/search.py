"""
Interactive Industrial Diagnostic Search CLI
============================================
Author: Huang Feng & Hermes Agent
License: PolyForm Noncommercial License 1.0.0

Entry point for two-tier know-how retrieval:

    python3 -m miner.search --db mock_emails.db "5.99寸 M2 过孔边缘腐蚀超标是什么原因？"

Shows whether the answer came from the L1 crystal cache (milliseconds,
zero full-text cost) or triggered an L2 deep dive (FTS5 + thread assembly),
including confidence, evidence grade, and Message-ID anchored citations.
"""

import argparse
import json
import sys

from miner.hybrid_router import HybridRouter


def format_response(result: dict) -> str:
    lines = []
    lines.append("=" * 78)
    lines.append(f"🔍 Query: {result['query']}")
    fp = result.get("fingerprint", {})
    lines.append(f"🏭 Plant fingerprint: layers={fp.get('layers')} stations={fp.get('stations')} "
                 f"equipment={fp.get('equipment_ids')} defects={fp.get('defect_codes')}")
    lines.append("=" * 78)

    if result["route"] == "L1_CACHE_HIT":
        ans = result["answer"]
        lines.append(f"⚡ ROUTE: L1 Knowledge Crystal Cache Hit (confidence: {result['confidence']})")
        lines.append("-" * 78)
        lines.append(f"[Incident]   {ans.get('incident_id')}")
        lines.append(f"[Symptom]    {ans.get('symptom')}")
        lines.append(f"[真因]  {ans.get('ground_truth_mechanism')}")
        lines.append(f"[PCA 对策]   {ans.get('pca_action')}")
        lines.append(f"[DFM Rule]   {ans.get('dfm_rule')}")
        lines.append(f"[Evidence]   Grade {ans.get('evidence_grade')}")
        try:
            anchors = json.loads(ans.get("evidence_anchor") or "[]")
            for a in anchors[:3]:
                lines.append(f"  ↳ cite: {a.get('message_id')} | {a.get('quote', a.get('subject', ''))[:80]}")
        except Exception:
            pass
    else:
        lines.append(f"🤿 ROUTE: L2 Full-Text Deep Dive (L1 confidence only {result['confidence']}, "
                     f"below threshold)")
        dive = result.get("dive", {})
        lines.append("-" * 78)
        lines.append(f"[FTS5 scanned]  {dive.get('scanned_emails', 0)} candidate emails")
        for i, hit in enumerate(dive.get("hits", [])[:5], 1):
            lines.append(f"  [{i}] ({hit.get('date_str','?')}) {hit.get('subject','')[:60]}")
            lines.append(f"      from: {hit.get('from_addr','')} | msg: {hit.get('message_id','')}")
        lines.append(f"[Threads assembled] {len(dive.get('threads', []))}")
        for t in dive.get("threads", [])[:3]:
            lines.append(f"  ↳ thread {t['thread_key'][:40]}... ({t['message_count']} messages)")
        atts = dive.get("attachment_evidence", [])
        if atts:
            lines.append(f"[Attachment evidence] {len(atts)} files")
            for a in atts[:3]:
                lines.append(f"  ↳ {a['type']}: {a['attachment'][:60]}")
        if result.get("consolidated_crystal"):
            lines.append(f"[认知进化] Deep dive consolidated into L1 crystal: "
                         f"{result['consolidated_crystal']}")
    lines.append("=" * 78)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="knowhow-miner two-tier industrial diagnostic search")
    parser.add_argument("query", help="Natural language troubleshooting question")
    parser.add_argument("--db", default="mock_emails.db", help="Email index database path")
    parser.add_argument("--store", default="data/knowledge_store.db", help="L1 knowledge store path")
    parser.add_argument("--threshold", type=float, default=0.80, help="Confidence threshold")
    parser.add_argument("--json", action="store_true", help="Output raw JSON instead of text")
    args = parser.parse_args()

    router = HybridRouter(args.db, args.store, args.threshold)
    result = router.answer(args.query)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    else:
        print(format_response(result))

    return 0 if result else 1


if __name__ == "__main__":
    sys.exit(main())
