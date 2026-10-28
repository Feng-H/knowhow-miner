import sys
import json
import sqlite3
import argparse
from typing import List
from miner.cleaner import EmailCleaner, CleanedEmail
from miner.aggregator import ThreadAggregator, IncidentTimeline
from miner.validator import LogicValidator

def run_pipeline(db_path: str, keyword: str = "", limit: int = 200, output_file: str = "incident_timelines.json"):
    print(f"[1/4] Connecting to index database: {db_path}...")
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
    print(f"      Retrieved {len(rows)} matching email records.")

    print("[2/4] Cleaning headers, body text, extracting entities...")
    email_objects: List[CleanedEmail] = []
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
        email_objects.append(ce)

    print(f"[3/4] Aggregating DAG conversation trees and lifecycle timelines...")
    aggregator = ThreadAggregator(max_thread_gap_days=14.0)
    timelines = aggregator.aggregate(email_objects)
    print(f"      Clustered {len(email_objects)} emails into {len(timelines)} incident timelines.")

    # Filter out single trivial isolated emails to focus on actual discussions
    multi_step_incidents = [t for t in timelines if t.email_count >= 2]
    print(f"      Identified {len(multi_step_incidents)} multi-round engineering incidents.")

    print(f"[4/4] Serializing to {output_file}...")
    output_data = []
    for inc in multi_step_incidents:
        output_data.append({
            "incident_id": inc.incident_id,
            "title": inc.title,
            "email_count": inc.email_count,
            "duration_days": inc.duration_days,
            "lifecycle_stage": inc.lifecycle_stage,
            "products": inc.products,
            "chambers": inc.chambers,
            "defect_codes": inc.defect_codes,
            "emails": inc.emails
        })

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"\n Pipeline run complete! {len(output_data)} incidents exported to {output_file}.")
    if output_data:
        print("\n--- Top Incident Summary Preview ---")
        for inc in output_data[:5]:
            print(f"[{inc['incident_id']}] ({inc['lifecycle_stage']}) {inc['title']} | {inc['email_count']} emails | Duration: {inc['duration_days']} days | Chambers: {inc['chambers']}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="knowhow-miner: Extract manufacturing incident timelines.")
    parser.add_argument("--db", type=str, default="/home/ubuntu/fpd-work/qq_index.db", help="Path to SQLite index db")
    parser.add_argument("--keyword", type=str, default="", help="Filter keyword (e.g. ITO2, M2, Taper, 铝腐)")
    parser.add_argument("--limit", type=int, default=1000, help="Max emails to process")
    parser.add_argument("--output", type=str, default="/home/ubuntu/fpd-work/knowhow-miner/data/extracted_incidents.json")
    args = parser.parse_args()

    run_pipeline(args.db, args.keyword, args.limit, args.output)
