import re
from typing import Dict, Any, List, Optional, Tuple
from miner.aggregator import IncidentTimeline

class CausalExtractor:
    """
    Distills structured manufacturing causal quintets from aggregated incident timelines.
    """

    @classmethod
    def extract_incident_knowledge(cls, timeline: IncidentTimeline, parsed_attachments: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Synthesizes emails and parsed attachment slides into a structured causal entity.
        """
        all_text = []
        for em in timeline.emails:
            all_text.append(f"[{em['date']}] {em['subject']}\n{em.get('body_snippet', '')}")

        if parsed_attachments:
            for att in parsed_attachments:
                for s in att.get("slides", []):
                    if s.get("is_critical"):
                        all_text.append(f"[ATTACHMENT SLIDE] {s.get('text', '')}")

        full_incident_text = "\n\n".join(all_text)

        # 1. Symptom Extraction
        symptom = cls._extract_symptom(full_incident_text, timeline.title)

        # 2. Hypothesis & Department Disputes
        disputes = cls._extract_disputes(full_incident_text)

        # 3. Validation Probe
        probe = cls._extract_probe(full_incident_text)

        # 4. Root Causes (Dual-Layer: Internal vs External)
        internal_rc, external_rc = cls._extract_root_causes(full_incident_text)

        # 5. Permanent Corrective Action (PCA) & Recipe Offsets
        pca, recipe_offset = cls._extract_pca_and_recipe(full_incident_text)

        # 6. DFM Design Redline
        dfm_rule = cls._derive_dfm_rule(full_incident_text, internal_rc, pca)

        # 7. Verification Evidence
        verification = cls._extract_verification(full_incident_text)

        return {
            "incident_id": timeline.incident_id,
            "title": timeline.title,
            "duration_days": timeline.duration_days,
            "lifecycle_stage": timeline.lifecycle_stage,
            "products": timeline.products,
            "chambers": timeline.chambers,
            "defect_codes": timeline.defect_codes,
            "symptom": symptom,
            "disputes": disputes,
            "validation_probe": probe,
            "root_cause_internal": internal_rc,
            "root_cause_external": external_rc,
            "pca_countermeasure": pca,
            "recipe_offset": recipe_offset,
            "design_redline_derived": dfm_rule,
            "verification_evidence": verification
        }

    @classmethod
    def _extract_symptom(cls, text: str, title: str) -> str:
        symptom_patterns = [
            r"([^\n。]*?(?:CD偏大|CD偏小|CD均值漂移|铝腐蚀|断线|短路|Mura|剥离|残胶|针孔|Stage Mura)[^\n。]*?[。！!])",
            r"([^\n。]*?(?:超标|报警|OOC|OOS|良率骤降)[^\n。]*?[。！!])"
        ]
        for pat in symptom_patterns:
            m = re.search(pat, text)
            if m:
                return m.group(1).strip()
        return title

    @classmethod
    def _extract_disputes(cls, text: str) -> List[Dict[str, str]]:
        disputes = []
        patterns = [
            (r"([^\n。]*?排查[^\n。]*?(?:正常|未见异常|没问题)[^\n。]*?[。！!])", "Defense"),
            (r"([^\n。]*?怀疑[^\n。]*?(?:部门|机台|制程|来料)[^\n。]*?[。！!])", "FingerPointing")
        ]
        for pat, d_type in patterns:
            for m in re.finditer(pat, text):
                disputes.append({"type": d_type, "statement": m.group(1).strip()})
        return disputes[:4]

    @classmethod
    def _extract_probe(cls, text: str) -> Optional[str]:
        probe_patterns = [
            r"([^\n。]*?(?:涂黑|探针|试验片|DOE验证|Slot验证|临时措施|验证方法)[^\n。]*?[。！!])",
            r"([^\n。]*?(?:短循环|Shortloop|换桶验证|对比测试)[^\n。]*?[。！!])"
        ]
        for pat in probe_patterns:
            m = re.search(pat, text)
            if m:
                return m.group(1).strip()
        return None

    @classmethod
    def _extract_root_causes(cls, text: str) -> Tuple[str, Optional[str]]:
        internal_rc = "待深入工程复盘"
        external_rc = None

        # Internal Truth Patterns
        internal_patterns = [
            r"([^\n。]*?(?:公差链断裂|未能完全覆盖|Overlay偏移|氯离子|氯残留|原料配比|感度变慢|驻波干涉|膜厚干涉|铁挡板腐蚀|温控失准)[^\n。]*?[。！!])",
            r"([^\n。]*?(?:真因|根本原因|物理机理)[^\n。]*?[。！!])"
        ]
        for pat in internal_patterns:
            m = re.search(pat, text)
            if m:
                internal_rc = m.group(1).strip()
                break

        # External 8D Excuse Patterns
        external_patterns = [
            r"([^\n。]*?(?:保养未及时|偶发性微粒|环境异物|临近PM周期|人员作业不规范)[^\n。]*?[。！!])"
        ]
        for pat in external_patterns:
            m = re.search(pat, text)
            if m:
                external_rc = m.group(1).strip()
                break

        return internal_rc, external_rc

    @classmethod
    def _extract_pca_and_recipe(cls, text: str) -> Tuple[str, Dict[str, Any]]:
        pca = "优化工艺窗口"
        offsets = {}

        pca_patterns = [
            r"([^\n。]*?(?:改版|Sizing Out|增大包边|补偿|PR Ashing|灰化|进料内控|梯度刻蚀|固化POR)[^\n。]*?[。！!])",
            r"([^\n。]*?(?:对策|根治措施|结案方案)[^\n。]*?[。！!])"
        ]
        for pat in pca_patterns:
            m = re.search(pat, text)
            if m:
                pca = m.group(1).strip()
                break

        # Extract numeric offsets
        m_offset = re.search(r"(?:补偿|Sizing Out|调整|增加|偏移)\s*([0-9.]+)\s*(μm|nm|Å|mJ|°C)", text)
        if m_offset:
            offsets["value"] = float(m_offset.group(1))
            offsets["unit"] = m_offset.group(2)

        return pca, offsets

    @classmethod
    def _derive_dfm_rule(cls, text: str, root_cause: str, pca: str) -> Optional[Dict[str, Any]]:
        if "过孔" in text or "ILD" in text or "包边" in text or "Enclosure" in text or "腐蚀" in text:
            return {
                "rule_id": "DFM-VIA-ENC-001",
                "category": "Via_Enclosure_Margin",
                "requirement": "Metal layer must enclose underlying Via by Enclosure_Margin >= (Tol_Via + Tol_Metal)/2 + Max_Overlay",
                "derived_action": "Force Sizing Out >= 1.5μm around ILD/PV contacts."
            }
        elif "干涉" in text or "ITO" in text or "膜厚" in text:
            return {
                "rule_id": "DFM-OPT-INT-002",
                "category": "Thin_Film_Swing_Curve",
                "requirement": "Target transparent electrode film thickness must lock at Swing Curve extrema (zero derivative) to eliminate 0.1μm CD swing per 200Å variation.",
                "derived_action": "Lock ITO PVD target at d = λ/(4n) extrema."
            }
        return None

    @classmethod
    def _extract_verification(cls, text: str) -> str:
        ver_patterns = [
            r"([^\n。]*?(?:良率恢复|点亮测试合格|腐蚀消除|结案 Release|恢复正常|验证有效|闭环)[^\n。]*?[。！!])"
        ]
        for pat in ver_patterns:
            m = re.search(pat, text)
            if m:
                return m.group(1).strip()
        return "持续监控中"
