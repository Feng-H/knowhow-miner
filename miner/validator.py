import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class ValidationReport:
    is_valid: bool
    score: int  # 0 to 100
    errors: List[str]
    warnings: List[str]
    flags: Dict[str, bool]

class LogicValidator:
    """
    Epistemological Quality Gates for Industrial Knowledge Mining (通用工程认识论质量门禁):
    
    This validator enforces methodological soundness independent of concrete industrial domains
    (FPD, semiconductors, battery chemistry, medical devices, metallurgy, etc.):
    
    1. Causal Decoupling: Flags conflation of customer-facing defensive narratives (4M excuses)
       vs true internal physical/first-principles mechanisms.
    2. Parsimony & Single-Point Trigger (Occam's Razor): Detects whether attribution isolates
       a verifiable single-point operational change vs generalized multi-variable noise.
    3. Observability Shift vs Physical Degradation: Distinguishes physical degradation from
       metrological changes (station relocation, phase transformation shrinkage, baseline shift).
    4. Decision State Machine Completeness (RULE-PAR-05): Verifies that an incident is captured
       as a 4-stage cognitive trajectory:
       - Initial Trigger & Fab Noise
       - First-Principles Deduction (Hypothesis Pruning)
       - Tactical Compromise (Line continuity trade-off)
       - Strategic PCA & Redline Lock
    5. Actionability & Closed-Loop Verification: Mandates mathematical design rule / quantifiable
       recipe offset and verifiable recovery evidence.
    """
    
    # Generic customer-facing defense excuses (management boilerplate across industries)
    CUSTOMER_EXCUSE_PATTERNS = [
        r"保养未及时|PM未到位|临近PM周期",
        r"偶发性微粒|环境偶发波动|温湿度微漂移",
        r"操作失误|人员培训不足|员工意识不强",
        r"多因素复合影响|4M复合因素|多重微弱变量共振",
        r"未按SOP执行|流程落实不到位",
        r"management composite|environmental fluctuation|routine PM variance"
    ]

    # Universal Single-Point Physical Change Triggers (Single degree of freedom shift)
    PARSIMONY_PHYSICAL_PATTERNS = [
        r"流量|高度|流速|气流|压差|开度|间隙",
        r"卡滞|轴承|轴肩|碰撞|阻尼|刚性接触",
        r"温差|漏热|热沉|接触温降|热传导",
        r"配方继承|孤岛配方|零点漂移|基准偏移",
        r"结晶|挂胶|结皮|干胶|喷孔堵塞|析出",
        r"flow|height|clearance|stiction|bearing|offset|drift|clog|stasis|inherit"
    ]

    # Metrology & Observability Shift Indicators (Measurement condition vs machine reality)
    VISIBILITY_SHIFT_PATTERNS = [
        r"站点.*(变更|后移|迁移|切换)",
        r"固化.*(收缩|体积收缩|相变|析出)",
        r"脱溶剂.*(干涉|显形|放大)",
        r"量测坐标.*(段差|边缘|台阶)",
        r"假报警|虚警|规格误套用|基准不一致",
        r"station relocation|phase change|shrinkage|optical phase|false alarm|metrology shift"
    ]

    # Ground Truth Physics & Causal Signatures
    INTERNAL_GROUND_TRUTH_PATTERNS = [
        r"腐蚀|反应|化学侵蚀|自催化|溶胀|水解|氧化",
        r"干涉|相消|光程差|驻波|相位",
        r"原料配比|分子量|门槛|活化能|感度|浓度突变",
        r"公差链|裕量不足|覆盖失效|对位极限|叠加超差",
        r"批次切换|换桶|源头变更|原料批次",
        r"热场不均|局部温漂|相变收缩|应力集中|微裂纹",
        r"corrosion|autocatalysis|interference|tolerance stack|enclosure margin|batch shift"
    ]

    @classmethod
    def validate_causal_triplet(cls, triplet: Dict[str, Any], bounds_spec: Optional[Dict[str, tuple]] = None) -> ValidationReport:
        errors = []
        warnings = []
        score = 100
        flags = {
            "has_customer_excuse": False,
            "has_ground_truth": False,
            "is_closed_loop": False,
            "has_actionable_offset": False,
            "is_parsimonious_physical": False,
            "is_visibility_shift": False,
            "has_decision_state_machine": False
        }

        # 1. Decision State Machine Trajectory (RULE-PAR-05: Context -> Deduction -> Trade-off -> Lock)
        traj = triplet.get("decision_trajectory") or {}
        if isinstance(traj, dict) and traj.get("initial_trigger_noise") and traj.get("first_principles_deduction"):
            flags["has_decision_state_machine"] = True

        # 2. Check required core fields
        root_cause = str(triplet.get("root_cause") or triplet.get("root_cause_internal") or "")
        symptom = str(triplet.get("symptom", ""))
        pca = str(triplet.get("pca_countermeasure") or triplet.get("pca_permanent_action") or "")
        verification = str(triplet.get("verification_evidence", ""))

        if not triplet.get("incident_id"):
            errors.append("Missing required field: incident_id")
            score -= 30
        if not symptom:
            errors.append("Missing required field: symptom")
            score -= 30
        if not root_cause:
            errors.append("Missing required field: root_cause")
            score -= 30

        # 3. Check Customer Defense vs Internal Reality
        for pat in cls.CUSTOMER_EXCUSE_PATTERNS:
            if re.search(pat, root_cause) or re.search(pat, pca):
                flags["has_customer_excuse"] = True
                warnings.append(f"Possible customer-facing defense excuse detected: '{pat}'. Verify if genuine root cause exists.")
                score -= 10
                break

        for pat in cls.INTERNAL_GROUND_TRUTH_PATTERNS:
            if re.search(pat, root_cause, re.I):
                flags["has_ground_truth"] = True
                break

        # RULE-PAR-01: Parsimony check (anti-conflation of composite 4M narratives)
        for pat in cls.PARSIMONY_PHYSICAL_PATTERNS:
            if re.search(pat, root_cause, re.I) or re.search(pat, pca, re.I):
                flags["is_parsimonious_physical"] = True
                flags["has_ground_truth"] = True
                break

        # RULE-THM-02: Process visibility shift detection (station relocation / phase contrast)
        for pat in cls.VISIBILITY_SHIFT_PATTERNS:
            if re.search(pat, root_cause, re.I) or re.search(pat, symptom, re.I):
                flags["is_visibility_shift"] = True
                break

        # 4. Check Actionable Recipe / Design Redline
        if triplet.get("recipe_offset") or triplet.get("design_redline") or triplet.get("design_redline_derived"):
            flags["has_actionable_offset"] = True
        else:
            warnings.append("No quantifiable recipe offset or design redline rule derived.")
            score -= 15

        # 5. Check Closed Loop Verification
        if verification and any(kw in verification for kw in ["良率", "恢复", "有效", "OK", "合格", "消除", "收敛", "达标", "0.2"]):
            flags["is_closed_loop"] = True
        else:
            warnings.append("Unverified resolution: missing clear yield recovery or re-inspection evidence.")
            score -= 15

        # 6. Domain-specific physical boundary sanity (injected externally via bounds_spec, never hardcoded)
        if bounds_spec:
            offsets = triplet.get("recipe_offset", {})
            if isinstance(offsets, dict):
                for param, val in offsets.items():
                    param_lower = param.lower()
                    for bound_name, (b_min, b_max) in bounds_spec.items():
                        if bound_name.lower() in param_lower:
                            try:
                                num_val = float(re.findall(r"[-+]?\d*\.\d+|\d+", str(val))[0])
                                if not (b_min <= num_val <= b_max):
                                    errors.append(f"Physical parameter out-of-bounds: {param} = {num_val} (Allowed: {b_min} ~ {b_max})")
                                    score -= 25
                            except Exception:
                                pass

        score = max(0, score)
        is_valid = len(errors) == 0 and score >= 60

        return ValidationReport(
            is_valid=is_valid,
            score=score,
            errors=errors,
            warnings=warnings,
            flags=flags
        )
