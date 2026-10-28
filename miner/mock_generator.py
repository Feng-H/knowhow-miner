"""
Mock Data Generator for knowhow-miner.
Generates an anonymized, synthetic SQLite database mimicking FPD manufacturing emails
so external users can run and test the pipeline without access to proprietary data.
"""

import sqlite3
import json
from datetime import datetime, timedelta

def create_mock_db(db_path: str = "mock_emails.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS emails")
    c.execute("""
        CREATE TABLE emails (
            source_folder TEXT,
            seq_num INTEGER,
            message_id TEXT,
            date_str TEXT,
            from_addr TEXT,
            to_addr TEXT,
            subject TEXT,
            has_attachments INTEGER,
            attachment_names TEXT,
            body_preview TEXT,
            mbox_chunk TEXT,
            fetched_at TEXT
        )
    """)

    base_time = datetime(2017, 10, 10, 9, 0, 0)

    # 1. M2 Al Corrosion Incident (3 rounds)
    m2_emails = [
        (
            "inbox", 1, "<m2_01@mock>",
            base_time.strftime("%a, %d %b %Y %H:%M:%S +0800"),
            "PI_Lead <engineer_pi@fab.mock>",
            "Array_Photo <photo_team@fab.mock>",
            "【G6】17603 AZ99(M2铝腐蚀)超标！",
            1, json.dumps(["ILD孔边铝腐蚀异常调查.pptx"]),
            "PI 反馈 M2 刻蚀后出现铝腐蚀聚集，多出现在 ILD 孔边黑色腐蚀，Poly 左侧过孔尤为严重。请排查！",
            "mock_chunk_0.mbox", "2017-10-10"
        ),
        (
            "inbox", 2, "<m2_02@mock>",
            (base_time + timedelta(hours=3)).strftime("%a, %d %b %Y %H:%M:%S +0800"),
            "DET_Lead <engineer_det@fab.mock>",
            "Array_Photo <photo_team@fab.mock>",
            "答复: 【G6】17603 AZ99(M2铝腐蚀)超标！",
            0, "[]",
            "DET 排查：Chamber 无明显机差，主要集中在 5.99 和 5.93 两款新产品。对比图纸发现 M2 PHT 未能完全覆盖 ILD 孔，Overlay 偏移导致孔边干刻暴露！",
            "mock_chunk_0.mbox", "2017-10-10"
        ),
        (
            "inbox", 3, "<m2_03@mock>",
            (base_time + timedelta(days=2)).strftime("%a, %d %b %Y %H:%M:%S +0800"),
            "Photo_Engineer <engineer_photo@fab.mock>",
            "PI_Lead <engineer_pi@fab.mock>",
            "答复: 答复: 【G6】17603 AZ99(M2铝腐蚀)超标！结案处理",
            0, "[]",
            "已确认新版 Mask 对 M2 过孔处实施单边 Sizing Out 1.5μm 补偿，试产批次点亮测试合格，腐蚀消除，良率恢复正常，结案 Release。",
            "mock_chunk_0.mbox", "2017-10-12"
        )
    ]

    # 2. ITO2 CD Drift Incident (3 rounds)
    ito2_emails = [
        (
            "inbox", 4, "<ito2_01@mock>",
            (base_time + timedelta(days=10)).strftime("%a, %d %b %Y %H:%M:%S +0800"),
            "QA_Lead <qa_lead@fab.mock>",
            "Photo_Team <photo_team@fab.mock>",
            "5.99 ITO2 CD 均值整体偏大报警",
            0, "[]",
            "Inline 监控显示 5.99 ITO2 CD 均值从 2.62μm 阶跃漂移至 2.69μm，超 OOC 管控线，已持卡！",
            "mock_chunk_0.mbox", "2017-10-20"
        ),
        (
            "inbox", 5, "<ito2_02@mock>",
            (base_time + timedelta(days=10, hours=4)).strftime("%a, %d %b %Y %H:%M:%S +0800"),
            "Photo_Engineer <engineer_photo@fab.mock>",
            "QA_Lead <qa_lead@fab.mock>",
            "答复: 5.99 ITO2 CD 均值整体偏大报警",
            1, json.dumps(["CD波动调查.pptx"]),
            "排查机台曝光 Dose、显影液浓度及 Pre-bake 温度完全稳定。时间戳比对发现本次跳跃 100% 对应供胶系统换桶时刻，光阻批次切换至 M18，感度 Eth 由 +0.9% 突降至 -0.6%！",
            "mock_chunk_0.mbox", "2017-10-20"
        ),
        (
            "inbox", 6, "<ito2_03@mock>",
            (base_time + timedelta(days=13)).strftime("%a, %d %b %Y %H:%M:%S +0800"),
            "Material_Lead <material_lead@fab.mock>",
            "Photo_Team <photo_team@fab.mock>",
            "答复: 答复: 5.99 ITO2 CD 均值整体偏大报警_供应商管控结案",
            0, "[]",
            "供应商已承认原料配比擅改导致感度变慢，已紧急下线异常桶，并建立进料 Eth 极窄窗口（+0.2%）卡控，全线 CD 均值恢复 2.62μm 基准，验证有效结案。",
            "mock_chunk_0.mbox", "2017-10-23"
        )
    ]

    for item in m2_emails + ito2_emails:
        c.execute("""
            INSERT INTO emails (
                source_folder, seq_num, message_id, date_str, from_addr, to_addr, 
                subject, has_attachments, attachment_names, body_preview, mbox_chunk, fetched_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, item)

    conn.commit()
    conn.close()
    print(f"Mock database created successfully at: {db_path} (6 emails, 2 verified incident clusters)")

if __name__ == "__main__":
    create_mock_db()
