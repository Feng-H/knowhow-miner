"""
Industrial Authority & Decision Weighting Engine
================================================
Author: Huang Feng & Hermes Agent
License: PolyForm Noncommercial License 1.0.0

This module ensures that email participants are NOT blindly stripped.
Instead of wiping names as useless noise, it computes an 'Authority Weight'
based on:
1. Technical Decision Role (Module Lead, Process Owner, Key Problem Solver)
2. Thread Conclusiveness (Who said '按此执行', '同意', '最终方案', '锁定Recipe')
3. Cross-Email Consistency (Using persistent pseudonyms like [Lead_PHT_Huang]
   to preserve decision chains across 22,000 emails while protecting personal PII).
"""

import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class PersonaProfile:
    pseudonym: str
    department: str
    role_type: str  # TECH_LEAD, MODULE_OWNER, INTEGRATION_PI, OPERATOR, BOT
    authority_weight: float  # 0.1 to 1.0
    known_domains: List[str]

class AuthorityWeightEngine:
    """
    Tracks and weights engineering decision-makers across email threads.
    Treats tech leads and process owners as primary truth anchors.
    """

    # Key Decision-Maker Mapping (Pseudonymized for privacy, high authority)
    PERSONA_REGISTRY: Dict[str, PersonaProfile] = {
        # Track & Yellow Light Tech Leads
        "feng_huang": PersonaProfile("Lead_Track_Huang", "PHT_TRK", "TECH_LEAD", 1.0, ["PR", "Slit_Coater", "CD", "VCD", "DP", "PLN", "AZ99"]),
        "jinrong_xu": PersonaProfile("Lead_Photo_Xu", "PHT", "TECH_LEAD", 0.95, ["Exposure", "Stepper", "Overlay", "DOF", "Lens"]),
        "shihua_jiang": PersonaProfile("Lead_Array_Jiang", "ARRAY_MFG", "MODULE_OWNER", 0.90, ["Inline_Flow", "Capacity", "Split_Lot"]),
        "zhihong_liao": PersonaProfile("Lead_Etch_Liao", "DET", "TECH_LEAD", 0.95, ["Dry_Etch", "ICP", "Taper", "Over_Etch", "STR"]),
        "xinrong_lu": PersonaProfile("Lead_ThinFilm_Lu", "CVD_PVD", "TECH_LEAD", 0.95, ["Sputter", "PECVD", "Target", "Peeling", "Stress"]),
        "shunjin_zhu": PersonaProfile("Lead_PI_Zhu", "PI", "INTEGRATION_PI", 0.95, ["Process_Window", "PCCB", "Yield", "DOE"]),
        "junzheng_li": PersonaProfile("Lead_Device_Li", "EQ_DEV", "MODULE_OWNER", 0.85, ["Machine_Set", "Recipe", "Priority"]),

        # Automated Systems / Bots (Low Authority for engineering truth, High for facts)
        "xm_cim_eda": PersonaProfile("System_EDA", "CIM", "BOT", 0.3, ["Alarm", "FDC", "Sensor"]),
        "xm_cim_mes": PersonaProfile("System_MES", "CIM", "BOT", 0.3, ["Dispatch", "Hold", "Release"]),
        "xm_cim_pms": PersonaProfile("System_PMS", "CIM", "BOT", 0.3, ["Maintenance", "PM"]),
    }

    DECISION_SIGNALS = [
        (re.compile(r"(?:同意(?:你的意见|方案|验证)?|批准|按此执行|以[此这]为准|定案|正式开始)"), 1.5, "FINAL_APPROVAL"),
        (re.compile(r"(?:锁定(?:recipe|参数|机台)|禁止(?:使用|生产)|暂时删除(?:站点)?|只在\w+生产)"), 1.4, "DISPATCH_LOCK"),
        (re.compile(r"(?:不同意|不能改动|严禁|不可修改)"), 1.3, "REJECTION_CONSTRAINT"),
        (re.compile(r"(?:请确认原因|到底是什么原因|为何又|有争议|推诿)"), 0.8, "DISPUTE_QUESTION"),
    ]

    @classmethod
    def resolve_sender(cls, from_addr: str) -> Dict[str, Any]:
        """
        Resolves a sender address to their pseudonym, domain authority, and department.
        Does NOT wipe the sender; normalizes them to an identifiable industrial persona.
        """
        if not from_addr:
            return {"pseudonym": "Unknown_Engineer", "authority": 0.5, "role": "ENGINEER", "dept": "UNKNOWN"}

        addr_lower = from_addr.lower()

        # Check registered personas
        for key, profile in cls.PERSONA_REGISTRY.items():
            if key in addr_lower:
                return {
                    "pseudonym": profile.pseudonym,
                    "authority": profile.authority_weight,
                    "role": profile.role_type,
                    "dept": profile.department,
                    "domains": profile.known_domains
                }

        # Check automated bots
        if "cim" in addr_lower or "noreply" in addr_lower or "admin" in addr_lower:
            return {"pseudonym": "System_Bot", "authority": 0.2, "role": "BOT", "dept": "CIM"}

        # Generic Team/Tech Accounts
        if "track" in addr_lower:
            return {"pseudonym": "Engineer_Track", "authority": 0.7, "role": "MODULE_ENGINEER", "dept": "PHT_TRK"}
        if "photo" in addr_lower or "pht" in addr_lower:
            return {"pseudonym": "Engineer_Photo", "authority": 0.7, "role": "MODULE_ENGINEER", "dept": "PHT"}
        if "det" in addr_lower or "etch" in addr_lower:
            return {"pseudonym": "Engineer_Etch", "authority": 0.7, "role": "MODULE_ENGINEER", "dept": "DET"}
        if "pi" in addr_lower:
            return {"pseudonym": "Engineer_PI", "authority": 0.75, "role": "INTEGRATION_PI", "dept": "PI"}

        return {"pseudonym": "Engineer_General", "authority": 0.5, "role": "ENGINEER", "dept": "MFG"}

    @classmethod
    def evaluate_thread_decision_weight(cls, from_addr: str, body_text: str) -> Dict[str, Any]:
        """
        Calculates the factual confidence weight of an email based on:
        Sender Base Authority x Decision Signal Multiplier.
        """
        sender_info = cls.resolve_sender(from_addr)
        base_authority = sender_info["authority"]
        detected_signals = []
        multiplier = 1.0

        for pat, mult, sig_type in cls.DECISION_SIGNALS:
            if pat.search(body_text):
                detected_signals.append(sig_type)
                multiplier = max(multiplier, mult)

        final_weight = min(1.0, round(base_authority * multiplier, 3))
        is_anchor_decision = ("FINAL_APPROVAL" in detected_signals or "DISPATCH_LOCK" in detected_signals) and base_authority >= 0.85

        return {
            "sender_pseudonym": sender_info["pseudonym"],
            "sender_role": sender_info["role"],
            "sender_dept": sender_info["dept"],
            "base_authority": base_authority,
            "decision_signals": detected_signals,
            "final_weight": final_weight,
            "is_anchor_decision": is_anchor_decision
        }
