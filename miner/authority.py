"""
Industrial Authority & Decision Weighting Engine
================================================
Author: Huang Feng & Hermes Agent
License: CC BY-NC-SA 4.0

This module maps engineering authority dynamically across time:
1. Static Registry Baseline (from DOE/NPI rosters as initial seeds)
2. Dynamic Linguistic & Semantic Role Detection (Detecting true Tech Leads via tone,
   directive structuring, experimental split parameters, and convergence closure)
3. Fluid Adaptation across Personnel Turnover & Fab Transitions (CSOT -> Tianma -> Intellimicro).
"""

import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class PersonaProfile:
    pseudonym: str
    department: str
    sub_module: str
    role_type: str  # TECH_LEAD, MODULE_OWNER, INTEGRATION_PI, PM, BOT
    authority_weight: float  # 0.1 to 1.0
    key_responsibilities: List[str]

class AuthorityWeightEngine:
    """
    Dynamically identifies true technical leaders from email tone and execution patterns,
    adapting to employee turnover without depending solely on static roster snapshots.
    """

    # Static Registry Baseline (Known ground-truth seeds)
    PERSONA_REGISTRY: Dict[str, PersonaProfile] = {
        "feng_huang": PersonaProfile("Lead_Track_Huang", "PHT", "TRACK", "TECH_LEAD", 1.0, ["PR涂胶均一性", "VCD/DP干燥", "CD控制", "膜厚规格", "AZ99防御"]),
        "shihua_jiang": PersonaProfile("Lead_Track_Jiang", "PHT", "TRACK", "MODULE_OWNER", 0.95, ["Track设备装机", "工艺验证", "材料评估"]),
        "xiangfa_huang": PersonaProfile("Lead_Photo_Huang", "PHT", "EXP", "TECH_LEAD", 0.95, ["批次对位稳定性", "Overlay对准", "DOF景深", "曝光场Mapping"]),
        "jinsen_yang": PersonaProfile("Lead_Photo_Yang", "PHT", "EXP", "MODULE_OWNER", 0.90, ["黄光设备固资", "机台配置", "日常异常仲裁"]),
        "xiuli_wang": PersonaProfile("Lead_Etch_Wang", "DET", "DRY_ETCH", "TECH_LEAD", 0.95, ["干刻各向异性", "坡度角Taper", "过孔瞎窗ILS04", "过刻ILS05"]),
        "dexiao_huang": PersonaProfile("Lead_Etch_Huang", "DET", "DRY_ETCH", "MODULE_OWNER", 0.90, ["干刻机台维护", "腔室RF放电"]),
        "haizhong_jin": PersonaProfile("Lead_Wet_Jin", "WET", "STRIP", "TECH_LEAD", 0.95, ["RE湿刻优化", "剥膜残胶STR06", "铝咬SPT01", "水渍残AZ15"]),
        "qi_zhou": PersonaProfile("Lead_Wet_Zhou", "WET", "STRIP", "MODULE_OWNER", 0.90, ["湿法药液浓度", "槽体清洗周期"]),
        "xinrui_shen": PersonaProfile("Lead_CVD_Shen", "DIFF", "CVD", "TECH_LEAD", 0.95, ["介质层成膜", "ILD针孔破洞AZ06", "CVD Particle"]),
        "xianbo_xie": PersonaProfile("Lead_CVD_Xie", "DIFF", "CVD", "MODULE_OWNER", 0.90, ["CVD腔体气相聚合", "成膜速率稳定"]),
        "chunfeng_zhao": PersonaProfile("Lead_PVD_Zhao", "DIFF", "PVD", "TECH_LEAD", 0.95, ["金属走线溅射", "靶材微爆飞溅PVD05", "膜层剥离Peeling PVD04"]),
        "ruihua_chen": PersonaProfile("Lead_PVD_Chen", "DIFF", "PVD", "MODULE_OWNER", 0.90, ["靶材更换周期", "放电打火PVD07"]),
        "ling_wang": PersonaProfile("Lead_ELA_Wang", "DIFF", "ELA", "TECH_LEAD", 0.95, ["多晶硅结晶Mura", "麻点PSL03", "激光爆斑PSL05"]),
        "xun_yang": PersonaProfile("Lead_IMP_Yang", "DIFF", "IMP", "TECH_LEAD", 0.95, ["掺杂浓度优化", "PMOS/CMOS阈值电压Vth漂移"]),
        "xueqin_zeng": PersonaProfile("Lead_IMP_Zeng", "DIFF", "IMP", "MODULE_OWNER", 0.90, ["离子注入剂量Uniformity"]),
        "yong_wu": PersonaProfile("Lead_Project_Wu", "RD_ACADEMY", "NPI", "TECH_LEAD", 1.0, ["整体直通良率改善", "多轮DOE方案制定"]),
        "hanyu_gu": PersonaProfile("Lead_PI_Gu", "PI", "INTEGRATION", "INTEGRATION_PI", 0.95, ["Array PI管理整合", "PCCB工艺变更评审"]),
        "ying_shen": PersonaProfile("Lead_PI_Shen", "RD_ACADEMY", "INTEGRATION", "INTEGRATION_PI", 0.95, ["整体器件PI设计", "跨制程窗口对齐"]),
        "wenxin_jiang": PersonaProfile("Lead_Design_Jiang", "RD_ACADEMY", "MASK_DESIGN", "TECH_LEAD", 0.95, ["柔性Mask版图设计", "DFM设计红线确认"]),
        "shihai_deng": PersonaProfile("Lead_Test_Deng", "TEST", "WAT_TEG", "TECH_LEAD", 0.95, ["Auto-probe测试结果Mapping", "电学参数异常"]),
        "xm_cim_eda": PersonaProfile("System_EDA", "CIM", "BOT", "BOT", 0.2, ["机台Sensor数据", "报警日志"]),
        "xm_cim_mes": PersonaProfile("System_MES", "CIM", "BOT", "BOT", 0.2, ["派工", "跳站", "卡匣Hold"]),
        "xm_cim_pms": PersonaProfile("System_PMS", "CIM", "BOT", "BOT", 0.2, ["PM保养计划"]),
    }

    # Dynamic Linguistic Patterns: True Technical Leader Tone
    DIRECTIVE_DISPATCH_PATTERNS = [
        re.compile(r"(?:条件如下|方案如下|安排如下|分工如下|参数设定如下|Split表如下)"),
        re.compile(r"(?:借机\s*\d+\s*(?:小时|h|min)|降温\s*\d+\s*小时|复机\s*\d+\s*min)"),
        re.compile(r"(?:slot\s*\d+(?:-\d+)?\s*(?:跑|run|测试|设定|条件))", re.IGNORECASE),
        re.compile(r"(?:按此执行|以[此这]为准|定案|正式开始|锁定(?:recipe|参数)|严格按此)"),
        re.compile(r"(?:不同意|不能改动|严禁|不可修改|必须由\w+供应)"),
        re.compile(r"(?:请\w{2,4}(?:安排|确认|跟进|排查|统计|测试))"),
    ]

    BROADCAST_NOTICE_PATTERNS = [
        re.compile(r"(?:全厂请知悉|请各位知悉|违纪情况|安全公告|节假日值班|体检名单|端午福利|班车安排)"),
        re.compile(r"(?:转发\s*[:：]\s*.*(?:通知|公告|宣导))"),
    ]

    @classmethod
    def analyze_linguistic_authority(cls, body_text: str) -> Dict[str, Any]:
        """
        Analyzes the linguistic tone and structural directives in the email body.
        Distinguishes between:
        - Tech Lead: Directive, parameters, split conditions, time allocation, boundary closures.
        - Broadcaster / Coordinator: Administrative notices, forwarding announcements, generic alerts.
        """
        directive_hits = sum(1 for p in cls.DIRECTIVE_DISPATCH_PATTERNS if p.search(body_text))
        notice_hits = sum(1 for p in cls.BROADCAST_NOTICE_PATTERNS if p.search(body_text))

        # Check for concrete technical parameters (CD, Dose, Recipe, Slot, etc.)
        param_density = len(re.findall(r"\b(?:\d+(?:\.\d+)?(?:um|μm|mJ|℃|s|min|小时|rpm|Torr)|slot\s*\d+|recipe\s*\w+)\b", body_text, re.IGNORECASE))

        is_directive_leader = directive_hits >= 2 or (directive_hits >= 1 and param_density >= 2)
        is_pure_notice = notice_hits >= 1 and directive_hits == 0 and param_density == 0

        dynamic_modifier = 0.0
        if is_directive_leader:
            dynamic_modifier = +0.25
        elif is_pure_notice:
            dynamic_modifier = -0.30

        return {
            "directive_hits": directive_hits,
            "notice_hits": notice_hits,
            "param_density": param_density,
            "is_directive_leader": is_directive_leader,
            "is_pure_notice": is_pure_notice,
            "dynamic_modifier": dynamic_modifier
        }

    @classmethod
    def resolve_sender(cls, from_addr: str, body_text: str = "") -> Dict[str, Any]:
        """
        Resolves a sender address to their pseudonym, domain authority, and department.
        Dynamically adjusts authority based on linguistic patterns in their body text.
        """
        if not from_addr:
            return {"pseudonym": "Unknown_Engineer", "authority": 0.5, "role": "ENGINEER", "dept": "UNKNOWN", "sub_module": "UNKNOWN"}

        addr_lower = from_addr.lower()

        # 1. Base from static registry
        base_authority = 0.5
        pseudonym = "Engineer_General"
        role = "ENGINEER"
        dept = "MFG"
        sub_module = "GENERAL"
        responsibilities = []

        for key, profile in cls.PERSONA_REGISTRY.items():
            if key in addr_lower:
                base_authority = profile.authority_weight
                pseudonym = profile.pseudonym
                role = profile.role_type
                dept = profile.department
                sub_module = profile.sub_module
                responsibilities = profile.key_responsibilities
                break
        else:
            # Domain guessing by mailbox alias
            if "cim" in addr_lower or "noreply" in addr_lower or "admin" in addr_lower:
                return {"pseudonym": "System_Bot", "authority": 0.2, "role": "BOT", "dept": "CIM", "sub_module": "SYS", "responsibilities": []}
            if "track" in addr_lower:
                base_authority = 0.7; pseudonym = "Engineer_Track"; role = "MODULE_ENGINEER"; dept = "PHT"; sub_module = "TRACK"
            elif "photo" in addr_lower or "pht" in addr_lower:
                base_authority = 0.7; pseudonym = "Engineer_Photo"; role = "MODULE_ENGINEER"; dept = "PHT"; sub_module = "EXP"
            elif "det" in addr_lower or "etch" in addr_lower:
                base_authority = 0.7; pseudonym = "Engineer_Etch"; role = "MODULE_ENGINEER"; dept = "DET"; sub_module = "DRY_ETCH"
            elif "wet" in addr_lower or "strip" in addr_lower:
                base_authority = 0.7; pseudonym = "Engineer_Wet"; role = "MODULE_ENGINEER"; dept = "WET"; sub_module = "STRIP"
            elif "pi" in addr_lower:
                base_authority = 0.75; pseudonym = "Engineer_PI"; role = "INTEGRATION_PI"; dept = "PI"; sub_module = "INTEGRATION"

        # 2. Dynamic Tone Adjustment (Handles Turnover & Non-Registry Leaders)
        ling_res = cls.analyze_linguistic_authority(body_text) if body_text else {"dynamic_modifier": 0.0, "is_directive_leader": False}
        adjusted_authority = min(1.0, max(0.2, round(base_authority + ling_res["dynamic_modifier"], 3)))

        # Promote unknown engineers who issue technical directives with parameters
        if ling_res.get("is_directive_leader") and role == "ENGINEER":
            role = "EMERGENT_TECH_LEAD"
            adjusted_authority = max(adjusted_authority, 0.90)

        return {
            "pseudonym": pseudonym,
            "authority": adjusted_authority,
            "base_authority": base_authority,
            "role": role,
            "dept": dept,
            "sub_module": sub_module,
            "responsibilities": responsibilities,
            "linguistic_analysis": ling_res
        }

    @classmethod
    def evaluate_thread_decision_weight(cls, from_addr: str, body_text: str) -> Dict[str, Any]:
        """
        Calculates the factual confidence weight of an email combining:
        Sender Dynamic Authority x Decision Signal Multiplier.
        """
        sender_info = cls.resolve_sender(from_addr, body_text)
        auth = sender_info["authority"]
        
        # Decision anchors: approval, dispatch lock, technical condition setup
        is_anchor_decision = (
            auth >= 0.85 and (
                sender_info["linguistic_analysis"].get("is_directive_leader", False) or
                "同意" in body_text or "按此执行" in body_text or "条件如下" in body_text
            )
        )

        return {
            "sender_pseudonym": sender_info["pseudonym"],
            "sender_role": sender_info["role"],
            "sender_dept": sender_info["dept"],
            "sub_module": sender_info["sub_module"],
            "final_weight": auth,
            "is_anchor_decision": is_anchor_decision,
            "linguistic_analysis": sender_info["linguistic_analysis"]
        }
