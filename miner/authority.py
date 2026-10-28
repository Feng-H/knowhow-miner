"""
Industrial Authority & Decision Weighting Engine
================================================
Author: Huang Feng & Hermes Agent
License: PolyForm Noncommercial License 1.0.0

This module maps engineering authority using Ground Truth from:
1. NPI Project Kick-off Roster: 《2016柔性良率改善小组人员名单》
2. DOE Craft Responsibility Roster: 《549柔性DOE Array工艺担当》
3. Production Meeting & PCCB Technical Reviews

It recognizes the true functional module leaders and process owners
rather than relying on naive email frequency.
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
    Tracks and weights engineering decision-makers across email threads.
    Treats tech leads and process owners as primary truth anchors.
    """

    # Ground Truth Module Owners (Extracted from 549柔性DOE & NPI Kick-off Lists)
    PERSONA_REGISTRY: Dict[str, PersonaProfile] = {
        # Track 涂胶显影担当
        "feng_huang": PersonaProfile("Lead_Track_Huang", "PHT", "TRACK", "TECH_LEAD", 1.0, ["PR涂胶均一性", "VCD/DP干燥", "CD控制", "膜厚规格", "AZ99防御"]),
        "shihua_jiang": PersonaProfile("Lead_Track_Jiang", "PHT", "TRACK", "MODULE_OWNER", 0.95, ["Track设备装机", "工艺验证", "材料评估"]),
        
        # PHOTO 曝光与黄光综合担当
        "xiangfa_huang": PersonaProfile("Lead_Photo_Huang", "PHT", "EXP", "TECH_LEAD", 0.95, ["批次对位稳定性", "Overlay对准", "DOF景深", "曝光场Mapping"]),
        "jinsen_yang": PersonaProfile("Lead_Photo_Yang", "PHT", "EXP", "MODULE_OWNER", 0.90, ["黄光设备固资", "机台配置", "日常异常仲裁"]),
        
        # DET 干刻担当
        "xiuli_wang": PersonaProfile("Lead_Etch_Wang", "DET", "DRY_ETCH", "TECH_LEAD", 0.95, ["干刻各向异性", "坡度角Taper", "过孔瞎窗ILS04", "过刻ILS05"]),
        "dexiao_huang": PersonaProfile("Lead_Etch_Huang", "DET", "DRY_ETCH", "MODULE_OWNER", 0.90, ["干刻机台维护", "腔室RF放电"]),
        
        # WET 湿法与剥膜担当
        "haizhong_jin": PersonaProfile("Lead_Wet_Jin", "WET", "STRIP", "TECH_LEAD", 0.95, ["RE湿刻优化", "剥膜残胶STR06", "铝咬SPT01", "水渍残AZ15"]),
        "qi_zhou": PersonaProfile("Lead_Wet_Zhou", "WET", "STRIP", "MODULE_OWNER", 0.90, ["湿法药液浓度", "槽体清洗周期"]),

        # CVD 薄膜沉积担当
        "xinrui_shen": PersonaProfile("Lead_CVD_Shen", "DIFF", "CVD", "TECH_LEAD", 0.95, ["介质层成膜", "ILD针孔破洞AZ06", "CVD Particle"]),
        "xianbo_xie": PersonaProfile("Lead_CVD_Xie", "DIFF", "CVD", "MODULE_OWNER", 0.90, ["CVD腔体气相聚合", "成膜速率稳定"]),

        # PVD 物理溅射镀膜担当
        "chunfeng_zhao": PersonaProfile("Lead_PVD_Zhao", "DIFF", "PVD", "TECH_LEAD", 0.95, ["金属走线溅射", "靶材微爆飞溅PVD05", "膜层剥离Peeling PVD04"]),
        "ruihua_chen": PersonaProfile("Lead_PVD_Chen", "DIFF", "PVD", "MODULE_OWNER", 0.90, ["靶材更换周期", "放电打火PVD07"]),

        # ELA / IMP 准分子退火与离子注入担当
        "ling_wang": PersonaProfile("Lead_ELA_Wang", "DIFF", "ELA", "TECH_LEAD", 0.95, ["多晶硅结晶Mura", "麻点PSL03", "激光爆斑PSL05"]),
        "xun_yang": PersonaProfile("Lead_IMP_Yang", "DIFF", "IMP", "TECH_LEAD", 0.95, ["掺杂浓度优化", "PMOS/CMOS阈值电压Vth漂移"]),
        "xueqin_zeng": PersonaProfile("Lead_IMP_Zeng", "DIFF", "IMP", "MODULE_OWNER", 0.90, ["离子注入剂量Uniformity"]),

        # PI / NPI 制程整合与研发领头人
        "yong_wu": PersonaProfile("Lead_Project_Wu", "RD_ACADEMY", "NPI", "TECH_LEAD", 1.0, ["整体直通良率改善", "多轮DOE方案制定"]),
        "hanyu_gu": PersonaProfile("Lead_PI_Gu", "PI", "INTEGRATION", "INTEGRATION_PI", 0.95, ["Array PI管理整合", "PCCB工艺变更评审"]),
        "ying_shen": PersonaProfile("Lead_PI_Shen", "RD_ACADEMY", "INTEGRATION", "INTEGRATION_PI", 0.95, ["整体器件PI设计", "跨制程窗口对齐"]),
        "wenxin_jiang": PersonaProfile("Lead_Design_Jiang", "RD_ACADEMY", "MASK_DESIGN", "TECH_LEAD", 0.95, ["柔性Mask版图设计", "DFM设计红线确认"]),
        
        # TEST 电性能测试担当
        "shihai_deng": PersonaProfile("Lead_Test_Deng", "TEST", "WAT_TEG", "TECH_LEAD", 0.95, ["Auto-probe测试结果Mapping", "电学参数异常"]),

        # 自动化系统 Bots
        "xm_cim_eda": PersonaProfile("System_EDA", "CIM", "BOT", "BOT", 0.2, ["机台Sensor数据", "报警日志"]),
        "xm_cim_mes": PersonaProfile("System_MES", "CIM", "BOT", "BOT", 0.2, ["派工", "跳站", "卡匣Hold"]),
        "xm_cim_pms": PersonaProfile("System_PMS", "CIM", "BOT", "BOT", 0.2, ["PM保养计划"]),
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
            return {"pseudonym": "Unknown_Engineer", "authority": 0.5, "role": "ENGINEER", "dept": "UNKNOWN", "sub_module": "UNKNOWN"}

        addr_lower = from_addr.lower()

        # Check registered ground-truth personas
        for key, profile in cls.PERSONA_REGISTRY.items():
            if key in addr_lower:
                return {
                    "pseudonym": profile.pseudonym,
                    "authority": profile.authority_weight,
                    "role": profile.role_type,
                    "dept": profile.department,
                    "sub_module": profile.sub_module,
                    "responsibilities": profile.key_responsibilities
                }

        # Check automated bots
        if "cim" in addr_lower or "noreply" in addr_lower or "admin" in addr_lower:
            return {"pseudonym": "System_Bot", "authority": 0.2, "role": "BOT", "dept": "CIM", "sub_module": "SYS"}

        # Generic Team/Tech Accounts
        if "track" in addr_lower:
            return {"pseudonym": "Engineer_Track", "authority": 0.7, "role": "MODULE_ENGINEER", "dept": "PHT", "sub_module": "TRACK"}
        if "photo" in addr_lower or "pht" in addr_lower:
            return {"pseudonym": "Engineer_Photo", "authority": 0.7, "role": "MODULE_ENGINEER", "dept": "PHT", "sub_module": "EXP"}
        if "det" in addr_lower or "etch" in addr_lower:
            return {"pseudonym": "Engineer_Etch", "authority": 0.7, "role": "MODULE_ENGINEER", "dept": "DET", "sub_module": "DRY_ETCH"}
        if "wet" in addr_lower or "strip" in addr_lower:
            return {"pseudonym": "Engineer_Wet", "authority": 0.7, "role": "MODULE_ENGINEER", "dept": "WET", "sub_module": "STRIP"}
        if "pi" in addr_lower:
            return {"pseudonym": "Engineer_PI", "authority": 0.75, "role": "INTEGRATION_PI", "dept": "PI", "sub_module": "INTEGRATION"}

        return {"pseudonym": "Engineer_General", "authority": 0.5, "role": "ENGINEER", "dept": "MFG", "sub_module": "GENERAL"}

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
            "sub_module": sender_info["sub_module"],
            "base_authority": base_authority,
            "decision_signals": detected_signals,
            "final_weight": final_weight,
            "is_anchor_decision": is_anchor_decision
        }
