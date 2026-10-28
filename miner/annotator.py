import re
from typing import Dict, Any, List, Set
from miner.cleaner import CleanedEmail

class DomainAnnotator:
    """
    Tags manufacturing entities, station roles, process layers, and defect types.
    """

    TECHNOLOGY_RULES = {
        "LTPS": [r"LTPS", r"G6", r"G5\.5", r"5\.99", r"5\.93", r"5\.46", r"ELA", r"Poly"],
        "a-Si": [r"a-Si", r"非晶硅", r"G8\.5", r"t1", r"t2"],
        "LTPO": [r"LTPO", r"IGZO", r"Oxide"],
        "OLED": [r"OLED", r"柔性", r"TFE"]
    }

    STATION_RULES = {
        "Photo": [r"Photo", r"黄光", r"曝光", r"PHT", r"Dose", r"Focus", r"Nikon", r"Canon", r"CD均一性", r"DOF"],
        "Track": [r"Track", r"涂胶", r"显影", r"Dev", r"Coater", r"Bake", r"Pre-bake", r"Hard-bake", r"HP\d+", r"TMAH", r"DP"],
        "DET": [r"DET", r"干刻", r"干法刻蚀", r"Chamber", r"RF", r"SF6", r"Cl2", r"BCl3", r"O2", r"Over-etch", r"刻蚀"],
        "WET": [r"WET", r"湿刻", r"湿法", r"草酸", r"Strip", r"剥膜", r"清洗", r"HF", r"CD Loss"],
        "ThinFilm_PVD": [r"PVD", r"溅射", r"Sputter", r"靶材", r"Mo", r"Al", r"ITO", r"成膜"],
        "ThinFilm_CVD": [r"CVD", r"PECVD", r"SiNx", r"SiO2", r"绝缘层", r"IMD", r"GI", r"ILD"],
        "Integration_PI": [r"PI", r"整合", r"良率", r"电学", r"点亮", r"RC", r"暗线", r"亮线"]
    }

    LAYER_RULES = {
        "M1_Gate": [r"\bM1\b", r"\bGate\b", r"栅极"],
        "M2_SourceDrain": [r"\bM2\b", r"\bS-D\b", r"\bSD\b", r"源漏"],
        "ITO1_Pixel": [r"\bITO1\b", r"下ITO", r"底层ITO"],
        "ITO2_Common": [r"\bITO2\b", r"上ITO", r"梳齿", r"爪子"],
        "Poly_Active": [r"\bPoly\b", r"\bACT\b", r"有源层", r"多晶硅"],
        "ILD_Dielectric": [r"\bILD\b", r"层间绝缘", r"介质层"],
        "PV_Passivation": [r"\bPV\b", r"钝化层"],
        "PLN_Planarization": [r"\bPLN\b", r"平坦化"]
    }

    DEFECT_RULES = {
        "CD_Drift": [r"CD偏大", r"CD偏小", r"CD漂高", r"CD异常", r"CD 均值", r"线宽"],
        "Al_Corrosion": [r"铝腐", r"腐蚀", r"AZ99", r"走线变细", r"发黑"],
        "Open_Break": [r"断线", r"\bOpen\b", r"开路"],
        "Short_Bridge": [r"短路", r"\bShort\b", r"桥连", r"\bBridge\b"],
        "Mura": [r"Mura", r"斑纹", r"手指Mura", r"条纹", r"暗影", r"Stage Mura"],
        "Particle": [r"Particle", r"异物", r"微粒", r"脏污", r"铁锈"],
        "Taper_Defect": [r"Taper", r"坡度", r"倒角", r"台阶覆盖", r"爬坡"]
    }

    @classmethod
    def annotate(cls, email: CleanedEmail) -> Dict[str, Any]:
        combined = f"{email.normalized_subject} \n {email.body_clean}"

        tags = {
            "technology": [],
            "stations": [],
            "layers": [],
            "defect_types": [],
            "dispute_involved": False
        }

        for tech, patterns in cls.TECHNOLOGY_RULES.items():
            if any(re.search(p, combined, re.IGNORECASE) for p in patterns):
                tags["technology"].append(tech)

        for station, patterns in cls.STATION_RULES.items():
            if any(re.search(p, combined, re.IGNORECASE) for p in patterns):
                tags["stations"].append(station)

        for layer, patterns in cls.LAYER_RULES.items():
            if any(re.search(p, combined, re.IGNORECASE) for p in patterns):
                tags["layers"].append(layer)

        for defect, patterns in cls.DEFECT_RULES.items():
            if any(re.search(p, combined, re.IGNORECASE) for p in patterns):
                tags["defect_types"].append(defect)

        # Dispute detection: multiple stations mentioned with defensive keywords
        if len(tags["stations"]) >= 2 and any(k in combined for k in ["排查无异常", "不是", "怀疑", "参数没变", "责任"]):
            tags["dispute_involved"] = True

        return tags
