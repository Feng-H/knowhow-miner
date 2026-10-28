import re
from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass, field
from miner.cleaner import CleanedEmail

@dataclass
class IncidentTimeline:
    incident_id: str
    title: str
    start_time: float
    end_time: float
    duration_days: float
    products: List[str]
    chambers: List[str]
    defect_codes: List[str]
    email_count: int
    emails: List[Dict] = field(default_factory=list)
    lifecycle_stage: str = "Investigation" # Initial -> Investigation -> Experiment -> Verification -> Closed

class ThreadAggregator:
    def __init__(self, max_thread_gap_days: float = 21.0):
        self.max_thread_gap_seconds = max_thread_gap_days * 86400.0

    def aggregate(self, email_list: List[CleanedEmail]) -> List[IncidentTimeline]:
        """
        Builds DAG threads from emails using:
        1. Explicit Message-ID -> In-Reply-To / References
        2. Normalized Subject + Entity Overlap (BCC Loop & Unthreaded Replies)
        3. Time-window clustering
        """
        # Sort chronologically
        sorted_emails = sorted(email_list, key=lambda e: e.timestamp)
        
        # 1. Map msg_id to cluster_id
        msg_to_cluster: Dict[str, int] = {}
        clusters: Dict[int, List[CleanedEmail]] = {}
        cluster_counter = 0

        # Helper to join clusters
        def merge_clusters(c1: int, c2: int) -> int:
            if c1 == c2:
                return c1
            # Merge c2 into c1
            for em in clusters[c2]:
                clusters[c1].append(em)
                msg_to_cluster[em.msg_id] = c1
            del clusters[c2]
            return c1

        # First pass: standard In-Reply-To / References
        for em in sorted_emails:
            assigned_cluster = None
            parent_ids = []
            if em.in_reply_to:
                parent_ids.append(em.in_reply_to)
            if em.references:
                parent_ids.extend(em.references)

            for pid in parent_ids:
                if pid in msg_to_cluster:
                    c_id = msg_to_cluster[pid]
                    if assigned_cluster is None:
                        assigned_cluster = c_id
                    else:
                        assigned_cluster = merge_clusters(assigned_cluster, c_id)

            if assigned_cluster is None:
                # New cluster
                assigned_cluster = cluster_counter
                clusters[assigned_cluster] = [em]
                cluster_counter += 1
            else:
                clusters[assigned_cluster].append(em)
            
            if em.msg_id:
                msg_to_cluster[em.msg_id] = assigned_cluster

        # Second pass: Merge by Normalized Subject & Time Window (handles BCC and cross-folder breaks)
        # Group remaining clusters by normalized subject
        subj_to_clusters: Dict[str, List[int]] = {}
        for c_id, c_emails in list(clusters.items()):
            # Find dominant subject
            subjects = [e.normalized_subject for e in c_emails if len(e.normalized_subject) > 3]
            if not subjects:
                continue
            dom_subj = subjects[0]
            # Strip spaces for fuzzy match
            dom_key = re.sub(r"[\s\-_，。！!？?【】\[\]（）()]+", "", dom_subj.lower())
            subj_to_clusters.setdefault(dom_key, []).append(c_id)

        # Merge clusters that share high substring similarity or entity overlap within time window
        all_keys = list(subj_to_clusters.keys())
        for i in range(len(all_keys)):
            k1 = all_keys[i]
            c_ids1 = subj_to_clusters.get(k1, [])
            if not c_ids1:
                continue
            main_cid = c_ids1[0]
            # Link other c_ids with identical or overlapping keys
            for j in range(i, len(all_keys)):
                k2 = all_keys[j]
                c_ids2 = subj_to_clusters.get(k2, [])
                if not c_ids2:
                    continue

                # Check if k1 and k2 share strong similarity (e.g. one contains another, length >= 6)
                is_match = (k1 == k2) or (len(k1) >= 6 and len(k2) >= 6 and (k1 in k2 or k2 in k1))
                if not is_match:
                    continue

                for next_cid in c_ids2:
                    if next_cid == main_cid:
                        continue
                    if next_cid not in clusters or main_cid not in clusters:
                        continue
                    t_end_main = max(e.timestamp for e in clusters[main_cid])
                    t_start_next = min(e.timestamp for e in clusters[next_cid])
                    t_end_next = max(e.timestamp for e in clusters[next_cid])
                    t_start_main = min(e.timestamp for e in clusters[main_cid])

                    time_gap = max(0.0, t_start_next - t_end_main, t_start_main - t_end_next)
                    if time_gap <= self.max_thread_gap_seconds:
                        main_cid = merge_clusters(main_cid, next_cid)

        # Convert clusters to IncidentTimelines
        timelines: List[IncidentTimeline] = []
        for c_id, c_emails in clusters.items():
            if not c_emails:
                continue
            c_emails.sort(key=lambda x: x.timestamp)
            start_t = c_emails[0].timestamp
            end_t = c_emails[-1].timestamp
            duration_days = round((end_t - start_t) / 86400.0, 2)
            
            # Aggregate metadata
            all_products = set()
            all_chambers = set()
            all_defects = set()
            all_lots = set()

            formatted_emails = []
            for em in c_emails:
                for k, v in em.entities.items():
                    if k == "products": all_products.update(v)
                    elif k == "chambers": all_chambers.update(v)
                    elif k == "defect_codes": all_defects.update(v)
                    elif k == "lots": all_lots.update(v)

                formatted_emails.append({
                    "seq_num": em.seq_num,
                    "date": em.date_str,
                    "timestamp": em.timestamp,
                    "from_role": "[ENGINEER]",
                    "subject": em.normalized_subject,
                    "attachments": em.attachments,
                    "body_snippet": em.body_clean[:500]
                })

            # Determine lifecycle
            lifecycle = "Initial"
            if len(c_emails) > 1:
                lifecycle = "Investigation"
            # If closing words exist in later emails
            last_text = (c_emails[-1].subject + " " + c_emails[-1].body_clean).lower()
            if any(w in last_text for w in ["结案", "release", "良率ok", "改善有效", "导入量产", "恢复正常", "闭环"]):
                lifecycle = "Closed"
            elif any(w in last_text for w in ["验证", "实验", "split", "testkey", "doe"]):
                lifecycle = "Experiment"

            timeline = IncidentTimeline(
                incident_id=f"INC-{c_id:04d}",
                title=c_emails[0].normalized_subject or "Untitled Manufacturing Incident",
                start_time=start_t,
                end_time=end_t,
                duration_days=duration_days,
                products=sorted(list(all_products)),
                chambers=sorted(list(all_chambers)),
                defect_codes=sorted(list(all_defects)),
                email_count=len(c_emails),
                emails=formatted_emails,
                lifecycle_stage=lifecycle
            )
            timelines.append(timeline)

        # Sort timelines by email count descending
        timelines.sort(key=lambda t: t.email_count, reverse=True)
        return timelines
