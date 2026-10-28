import sys
import os
import json
import sqlite3
import argparse
from typing import List, Dict, Any

from miner.cleaner import EmailCleaner, CleanedEmail
from miner.classifier import EmailClassifier
from miner.annotator import DomainAnnotator
from miner.aggregator import ThreadAggregator, IncidentTimeline
from miner.causal_extractor import CausalExtractor
from miner.validator import LogicValidator
from miner.graph_builder import ManufacturingKnowledgeGraph

def run_pipeline(
    db_path: str,
    keyword: str = "",
    limit: int = 500,
    output_dir: str = "/home/ubuntu/fpd-work/knowhow-miner/data",
    html_title: str = "FPD Array Know-How Causal Graph"
):
    os.makedirs(output_dir, exist_ok=True)
    print(f"============================================================")
    print(f"🏭 knowhow-miner: Full Industrial Knowledge Graph Pipeline")
    print(f"============================================================")

    # 1. Database Query
    print(f"[1/6] 📥 Connecting to index database: {db_path}...")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    query = """
        SELECT source_folder, seq_num, message_id, date_str, from_addr, to_addr, subject, body_preview, attachment_names, mbox_chunk
        FROM emails
    """
    params = []
    if keyword:
        query += " WHERE subject LIKE ? OR body_preview LIKE ? OR attachment_names LIKE ?"
        kw = f"%{keyword}%"
        params.extend([kw, kw, kw])
    query += " ORDER BY seq_num ASC LIMIT ?"
    params.append(limit)

    c.execute(query, params)
    rows = c.fetchall()
    print(f"      ✓ Retrieved {len(rows)} matching email records.")

    # 2. Cleaning & Anonymization
    print(f"[2/6] 🧹 Cleaning, anonymizing, and parsing headers/body...")
    raw_emails: List[CleanedEmail] = []
    for r in rows:
        source_folder, seq_num, message_id, date_str, from_addr, to_addr, subject, body_preview, att_names, mbox_chunk = r
        clean_subj = EmailCleaner.clean_subject(subject or "")
        clean_body = EmailCleaner.clean_body(body_preview or "")
        ts = EmailCleaner.parse_timestamp(date_str)
        entities = EmailCleaner.extract_entities(clean_body, clean_subj)

        atts = []
        if att_names:
            try:
                atts = json.loads(att_names)
            except Exception:
                atts = [att_names]

        msg_id = message_id or f"<{source_folder}_{seq_num}@local>"

        ce = CleanedEmail(
            msg_id=msg_id,
            in_reply_to=None,
            references=[],
            date_str=date_str or "",
            timestamp=ts,
            from_addr=from_addr or "",
            to_addrs=[to_addr or ""],
            cc_addrs=[],
            subject=subject or "",
            normalized_subject=clean_subj,
            body_clean=clean_body,
            attachments=atts,
            source_mbox=mbox_chunk or "",
            seq_num=seq_num,
            entities=entities
        )
        raw_emails.append(ce)

    # 3. Email Classification & Noise Filtering
    print(f"[3/6] 🏷️ Classifying emails, tagging domains, and filtering noise...")
    valid_emails: List[CleanedEmail] = []
    classification_counts: Dict[str, int] = {}
    annotations_map: Dict[int, Dict[str, Any]] = {}

    noise_count = 0
    for em in raw_emails:
        cat, conf, is_noise = EmailClassifier.classify(em)
        classification_counts[cat] = classification_counts.get(cat, 0) + 1

        if is_noise:
            noise_count += 1
            continue

        ann = DomainAnnotator.annotate(em)
        annotations_map[em.seq_num] = ann
        valid_emails.append(em)

    print(f"      ✓ Filtered out {noise_count} administrative noise emails.")
    print(f"      ✓ Classification breakdown: {classification_counts}")

    # 4. DAG Aggregation & Timeline Reconstruction
    print(f"[4/6] 🧩 Reconstructing DAG conversation trees and event lifecycles...")
    aggregator = ThreadAggregator(max_thread_gap_days=14.0)
    timelines = aggregator.aggregate(valid_emails)
    multi_step_incidents = [t for t in timelines if t.email_count >= 2]
    print(f"      ✓ Clustered into {len(multi_step_incidents)} multi-round manufacturing incidents.")

    # 5. Causal Fact & DFM Rule Extraction + Validation
    print(f"[5/6] 🔬 Distilling causal quintets, DFM rules, and enforcing physical validation...")
    causal_records = []
    valid_causal_records = []
    incident_annotations: Dict[str, Dict[str, Any]] = {}

    for inc in multi_step_incidents:
        # Aggregate tags for incident
        all_stations = set()
        all_layers = set()
        for em in inc.emails:
            s_num = em.get("seq_num")
            if s_num in annotations_map:
                ann = annotations_map[s_num]
                all_stations.update(ann.get("stations", []))
                all_layers.update(ann.get("layers", []))

        incident_annotations[inc.incident_id] = {
            "stations": list(all_stations),
            "layers": list(all_layers)
        }

        # Extract
        record = CausalExtractor.extract_incident_knowledge(inc)
        causal_records.append(record)

        # Validate
        val_report = LogicValidator.validate_causal_triplet(record)
        record["validation"] = {
            "is_valid": val_report.is_valid,
            "score": val_report.score,
            "warnings": val_report.warnings,
            "flags": val_report.flags
        }
        if val_report.is_valid:
            valid_causal_records.append(record)

    print(f"      ✓ Extracted {len(causal_records)} causal records ({len(valid_causal_records)} passed high-confidence validation).")

    # 6. Knowledge Graph Construction & HTML Visualization
    print(f"[6/6] 🕸️ Constructing Knowledge Graph and exporting interactive network...")
    kg = ManufacturingKnowledgeGraph()
    kg.build_from_causal_records(causal_records, incident_annotations)

    json_graph_path = os.path.join(output_dir, "knowledge_graph.json")
    html_graph_path = os.path.join(output_dir, "knowledge_graph.html")
    incidents_path = os.path.join(output_dir, "incidents.json")
    causal_path = os.path.join(output_dir, "causal_records.json")

    kg.export_json(json_graph_path)
    kg.export_interactive_html(html_graph_path, title=html_title)

    with open(incidents_path, "w", encoding="utf-8") as f:
        json.dump([
            {
                "incident_id": t.incident_id,
                "title": t.title,
                "email_count": t.email_count,
                "duration_days": t.duration_days,
                "lifecycle_stage": t.lifecycle_stage,
                "products": t.products,
                "chambers": t.chambers,
                "defect_codes": t.defect_codes,
                "emails": t.emails
            } for t in multi_step_incidents
        ], f, ensure_ascii=False, indent=2)

    with open(causal_path, "w", encoding="utf-8") as f:
        json.dump(causal_records, f, ensure_ascii=False, indent=2)

    print(f"\n============================================================")
    print(f"🎉 Pipeline Complete! Deliverables:")
    print(f"  - 📄 Incident Timelines:    {incidents_path}")
    print(f"  - 🔬 Causal Knowledge:      {causal_path}")
    print(f"  - 🌐 Graph (JSON):          {json_graph_path}")
    print(f"  - 📊 Interactive HTML Graph: {html_graph_path}")
    print(f"============================================================")

    # Top Graph Statistics
    print(f"Graph Metrics: {len(kg.nodes)} Nodes, {len(kg.edges)} Edges.")
    return html_graph_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="knowhow-miner: End-to-end industrial manufacturing know-how extraction pipeline.")
    parser.add_argument("--db", type=str, default="/home/ubuntu/fpd-work/qq_index.db", help="Path to SQLite index db")
    parser.add_argument("--keyword", type=str, default="", help="Filter keyword (e.g. ITO2, M2, Taper, 铝腐)")
    parser.add_argument("--limit", type=int, default=500, help="Max emails to process")
    parser.add_argument("--output_dir", type=str, default="/home/ubuntu/fpd-work/knowhow-miner/data", help="Output directory")
    args = parser.parse_args()

    run_pipeline(args.db, args.keyword, args.limit, args.output_dir)
