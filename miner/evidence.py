"""
Industrial Evidence Hierarchy & Multi-Modal Arbitration Engine
==============================================================
Author: Huang Feng & Hermes Agent
License: PolyForm Noncommercial License 1.0.0

Adapted from Forward Deployed Engineering (FDE) principles:
1. Five-Level Evidence Hierarchy (A-E Grades)
2. Conflict Arbitration Rules (Hard physical data > Leader directives > Disputes > Speculation)
3. Direct Citation Anchoring (Exact quote, slide location, message ID)
"""

from enum import Enum
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

class EvidenceGrade(Enum):
    GRADE_A = "A_AUTHORITY_DIRECTIVE"    # Tech Lead Anchor Decision / Signed SOP / Locked Recipe
    GRADE_B = "B_PHYSICAL_MEASUREMENT"   # Excel Split Table measurement (CD-SEM, Film THK, Log)
    GRADE_C = "C_MULTI_SOURCE_ALIGNMENT" # Multi-department cross-verified with valid physics
    GRADE_D = "D_SINGLE_DISPUTE_SPEC"    # Single engineer hypothesis / Unverified blame
    GRADE_E = "E_HEURISTIC_KEYWORD"      # Heuristic pattern / Regex guess

@dataclass
class EvidenceItem:
    grade: EvidenceGrade
    source_type: str  # EMAIL_BODY, EXCEL_SHEET, PPT_SLIDE, ALARM_LOG
    source_id: str    # Message-ID or filename
    location: str     # Line number, slide index, cell coordinate
    quote: str        # Exact raw quote / data value
    authority_score: float = 0.5
    confidence: float = 0.8
    meta: Dict[str, Any] = field(default_factory=dict)

class EvidenceArbiter:
    """
    Arbitrates conflicts across multi-source manufacturing inputs.
    Strictly forbids lower-grade evidence from overriding higher-grade truth.
    """

    GRADE_WEIGHTS = {
        EvidenceGrade.GRADE_A: 1.0,
        EvidenceGrade.GRADE_B: 0.95,
        EvidenceGrade.GRADE_C: 0.85,
        EvidenceGrade.GRADE_D: 0.50,
        EvidenceGrade.GRADE_E: 0.30
    }

    @classmethod
    def create_evidence(
        cls,
        grade: EvidenceGrade,
        source_type: str,
        source_id: str,
        location: str,
        quote: str,
        authority_score: float = 0.5,
        meta: Optional[Dict[str, Any]] = None
    ) -> EvidenceItem:
        return EvidenceItem(
            grade=grade,
            source_type=source_type,
            source_id=source_id,
            location=location,
            quote=quote.strip(),
            authority_score=authority_score,
            meta=meta or {}
        )

    @classmethod
    def arbitrate_conflicts(cls, claims: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Arbitrates conflicting root-cause claims or parameter values.
        Sorts claims by:
        1. Evidence Grade Weight (Grade A > Grade B > ...)
        2. Author Authority Score
        3. Citation presence
        """
        if not claims:
            return {"resolved": None, "conflict_status": "NO_CLAIMS"}

        def sort_key(item):
            ev: EvidenceItem = item.get("evidence")
            grade_weight = cls.GRADE_WEIGHTS.get(ev.grade, 0.0) if ev else 0.0
            auth_score = ev.authority_score if ev else 0.5
            has_quote = 1.0 if (ev and ev.quote) else 0.0
            return (grade_weight, auth_score, has_quote)

        sorted_claims = sorted(claims, key=sort_key, reverse=True)
        top_claim = sorted_claims[0]

        has_conflict = False
        if len(sorted_claims) > 1:
            second_claim = sorted_claims[1]
            # Check if claims contradict in conclusion
            if top_claim.get("conclusion") != second_claim.get("conclusion"):
                has_conflict = True

        top_evidence: Optional[EvidenceItem] = top_claim.get("evidence")
        arbitration_reason = "Default resolution"
        if top_evidence:
            arbitration_reason = (
                f"Selected {top_evidence.grade.name} from {top_evidence.source_id} "
                f"with authority {top_evidence.authority_score} over "
                f"{len(sorted_claims)-1} lower-priority alternatives."
            )

        return {
            "resolved_claim": top_claim,
            "has_conflict": has_conflict,
            "all_claims_ranked": sorted_claims,
            "arbitration_reason": arbitration_reason
        }
