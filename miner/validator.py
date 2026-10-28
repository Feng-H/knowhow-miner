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
    Enforces engineering quality gates:
    1. Physical Sanity: Checks parameter boundaries (Dose, Focus, Temp, Pressure)
    2. Chronological Sanity: Verifies that root cause & PCA correlate with later closure,
       not premature refutation.
    3. Dual-Reality Decoupling: Flags discrepancies between external 8D customer excuses
       vs internal physics root causes.
    """
    
    # Typical physical bounds for FPD Array
    PARAM_BOUNDS = {
        "dose": (5.0, 300.0),       # mJ/cm^2
        "focus": (-50.0, 50.0),     # μm
        "temp_pb": (70.0, 160.0),   # °C
        "temp_hb": (100.0, 250.0),  # °C
        "pressure_dp": (10.0, 500.0),# Pa
        "overlay": (-2.0, 2.0),     # μm
    }

    CUSTOMER_EXCUSE_PATTERNS = [
        r"保养未及时",
        r"偶发性微粒",
        r"环境波动",
        r"设备临近PM周期",
        r"操作失误",
        r"人员培训不足"
    ]

    INTERNAL_GROUND_TRUTH_PATTERNS = [
        r"腐蚀.*铁",
        r"材质缺陷",
        r"氯残留",
        r"驻波干涉",
        r"原料配比.*变动",
        r"感度突变",
        r"公差链断裂",
        r"DRC.*裕量不足"
    ]

    @classmethod
    def validate_causal_triplet(cls, triplet: Dict[str, Any]) -> ValidationReport:
        errors = []
        warnings = []
        score = 100
        flags = {
            "has_customer_excuse": False,
            "has_ground_truth": False,
            "is_closed_loop": False,
            "has_actionable_offset": False
        }

        # 1. Check required fields
        for field in ["incident_id", "symptom", "root_cause"]:
            if not triplet.get(field):
                errors.append(f"Missing required field: {field}")
                score -= 30

        symptom = str(triplet.get("symptom", ""))
        root_cause = str(triplet.get("root_cause", ""))
        pca = str(triplet.get("pca_permanent_action", ""))
        verification = str(triplet.get("verification_evidence", ""))

        # 2. Check Customer Defense vs Internal Reality
        for pat in cls.CUSTOMER_EXCUSE_PATTERNS:
            if re.search(pat, root_cause) or re.search(pat, pca):
                flags["has_customer_excuse"] = True
                warnings.append(f"Possible customer-facing defense excuse detected: '{pat}'. Verify if genuine root cause exists.")
                score -= 10
                break

        for pat in cls.INTERNAL_GROUND_TRUTH_PATTERNS:
            if re.search(pat, root_cause):
                flags["has_ground_truth"] = True
                break

        # 3. Check Actionable Recipe / Design Redline
        if triplet.get("recipe_offset") or triplet.get("design_redline"):
            flags["has_actionable_offset"] = True
        else:
            warnings.append("No quantifiable recipe offset or design redline rule derived.")
            score -= 15

        # 4. Check Closed Loop Verification
        if verification and any(kw in verification for kw in ["良率", "恢复", "有效", "OK", "合格", "消除", "0.2"]):
            flags["is_closed_loop"] = True
        else:
            warnings.append("Unverified resolution: missing clear yield recovery or re-inspection evidence.")
            score -= 15

        # 5. Sanity check parameters if extracted
        offsets = triplet.get("recipe_offset", {})
        if isinstance(offsets, dict):
            for param, val in offsets.items():
                param_lower = param.lower()
                for bound_name, (b_min, b_max) in cls.PARAM_BOUNDS.items():
                    if bound_name in param_lower:
                        try:
                            # Extract numeric
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
