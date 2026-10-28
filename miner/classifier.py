import re
from typing import Dict, Any, List, Tuple
from miner.cleaner import CleanedEmail

class EmailClassifier:
    """
    Classifies manufacturing emails into operational intents and filters administrative noise.
    """

    CATEGORIES = {
        "ALARM": [
            r"超标", r"报警", r"NG", r"异常", r"Hold", r"OOC", r"OOS", r"破损", r"报废",
            r"断线", r"短路", r"残留", r"Mura", r"偏大", r"偏小", r"漂高", r"突发", r"卡单"
        ],
        "DISPUTE": [
            r"排查.*正常", r"参数没有动", r"不是.*原因", r"怀疑.*部门", r"请.*确认", r"机差",
            r"推诿", r"建议.*调查", r"数据无异常", r"未见异常", r"责任部门", r"协助确认"
        ],
        "DOE_EXPERIMENT": [
            r"DOE", r"实验", r"Split", r"分件", r"Testkey", r"试产", r"验证", r"方案",
            r"条件", r"Slot", r"控片", r"Shortloop", r"Dummy", r"流片"
        ],
        "REPORT_8D": [
            r"8D", r"调查报告", r"分析报告", r"复盘", r"结案", r"Release", r"总结",
            r"真因", r"对策", r"改善状况", r"终结", r"闭环"
        ],
        "SHIFT_HANDOVER": [
            r"交接班", r"早会", r"交接", r"晚班", r"早班", r"产线情况", r"本日总结"
        ],
        "NOISE": [
            r"订餐", r"调休", r"放假", r"生日", r"水票", r"培训通知", r"催大家", r"请在本周五下班前",
            r"随便提几卡", r"发票", r"系统维护", r"测试邮件", r"退信", r"请勿回复"
        ]
    }

    @classmethod
    def classify(cls, email: CleanedEmail) -> Tuple[str, float, bool]:
        """
        Returns:
            category: ALARM, DISPUTE, DOE_EXPERIMENT, REPORT_8D, SHIFT_HANDOVER, NOISE
            confidence: 0.0 ~ 1.0
            is_noise: True if administrative noise without technical substance
        """
        combined = f"{email.normalized_subject} \n {email.body_clean}"
        
        # Check noise first
        noise_hits = sum(1 for p in cls.CATEGORIES["NOISE"] if re.search(p, combined, re.IGNORECASE))
        if noise_hits >= 1 and not any(k in combined for k in ["CD", "Dose", "Focus", "Taper", "Chamber", "Lot"]):
            return "NOISE", 0.9, True

        scores = {}
        for cat, patterns in cls.CATEGORIES.items():
            if cat == "NOISE":
                continue
            hits = sum(1 for p in patterns if re.search(p, combined, re.IGNORECASE))
            scores[cat] = hits

        sorted_cats = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_cat, top_score = sorted_cats[0]

        if top_score == 0:
            # Default fallback based on attachments
            if email.attachments:
                return "REPORT_8D", 0.5, False
            return "GENERAL_DISCUSSION", 0.4, False

        confidence = min(1.0, 0.4 + (top_score * 0.15))
        return top_cat, round(confidence, 2), False
