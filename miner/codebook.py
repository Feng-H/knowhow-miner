"""
FPD Multi-Fab Codebook & Metadata Dictionary (Tianma, CSOT, Intellimicro)
========================================================================
Author: Huang Feng & Hermes Agent
License: PolyForm Noncommercial License 1.0.0

This module serves as the primary factory dictionary for `knowhow-miner`.
It incorporates knowledge derived from:
1. Factory Defect Codebooks (Array Defect Code List(LTPS).xls, OLED缺陷限样.ppt)
2. Equipment & Routing Configurations (4.97 FHD 机台设置.xls, L1497B020APB03.xlsx)
3. New Hire Onboarding Exams & SOPs (G6 Track工程师/技术员入职考试题, 考题.docx, TCU/CDC/Titler课件)
4. Inter-departmental Asset & Workflow Rosters (各部门固资管理员名单（G5.5&G6）.xlsx)
"""

import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class DefectDefinition:
    code: str
    name_zh: str
    category: str
    station_default: str
    layer_hint: Optional[str] = None
    is_killer: bool = False
    can_repair: Optional[bool] = None
    description: str = ""

@dataclass
class OperationStation:
    op_code: str
    name: str
    layer: str
    step_type: str  # DEPO_AOI, PH_ADI, ET_AEI, ANNEAL_AOI, FINAL_AOI

@dataclass
class MachineDefinition:
    eq_id: str
    eq_type: str
    station_group: str
    vendor: str = ""
    description: str = ""

class FPDCodebook:
    """
    Standard Defect, Machine, Station & Department Dictionary.
    Used by Cleaner, Classifier, and Evaluator to recognize manufacturing tokens
    and prevent over-cleaning or misclassification.
    """

    # 1. Factory / Organization Codes
    FAB_CODES = {
        "A1": "厦门天马 G5.5/G6 Array 阵列厂",
        "F1": "厦门天马 CF 彩膜厂",
        "C1": "厦门天马 Cell 成盒制程厂",
        "M1": "厦门天马 Module 模组厂",
        "CSOT_T1": "华星光电 G8.5 T1 阵列厂",
        "CSOT_T2": "华星光电 G8.5 T2 阵列厂",
    }

    # 2. Department & Team Codes
    DEPARTMENT_CODES = {
        "PHT": "黄光光刻工程部 (Photolithography / Photo Team)",
        "TRK": "涂胶显影组 (Track Team)",
        "EXP": "曝光机组 (Exposure / Stepper Team)",
        "DET": "干法刻蚀工程部 (Dry Etch Team)",
        "WET": "湿法制程部 (Wet Etch & Strip Team)",
        "STR": "剥膜清洗组 (Strip Team)",
        "CVD": "化学气相沉积薄膜部 (Chemical Vapor Deposition Team)",
        "PVD": "物理溅射镀膜部 (Physical Vapor Deposition Team)",
        "DIFF": "薄膜扩散部",
        "ELA": "准分子激光退火组 (Excimer Laser Anneal)",
        "RTA": "快速热退火组 (Rapid Thermal Anneal)",
        "IMP": "离子注入组 (Ion Implantation Team)",
        "PI": "制程整合部 (Process Integration)",
        "TEST": "电性能测试部 (Array Test / TEG)",
        "CIM": "计算机集成制造 / MES 系统部",
        "DCC": "文件管制中心 (Document Control Center)",
        "EHS": "环境健康安全部",
    }

    # 3. Full Defect Codes Catalog (from Array Defect Code List & OLED缺陷限样)
    DEFECT_CATALOG: Dict[str, DefectDefinition] = {
        # AZ Universal Codes
        "AZ01": DefectDefinition("AZ01", "裂纹", "COMMON", "ALL", description="玻璃基板本体微裂纹 (Glass Crack)"),
        "AZ02": DefectDefinition("AZ02", "划伤", "COMMON", "ALL", description="表面机械性划伤 (Surface Scratch)"),
        "AZ03": DefectDefinition("AZ03", "玻璃碎屑", "COMMON", "ALL", description="板边碰撞碎屑 (Glass Chipping)"),
        "AZ04": DefectDefinition("AZ04", "黑斑", "COMMON", "ALL", description="局部发黑脏污 (Black Spot)"),
        "AZ05": DefectDefinition("AZ05", "沙状Defect", "COMMON", "ALL", description="细密颗粒散布缺陷"),
        "AZ06": DefectDefinition("AZ06", "ILD破洞", "DIELECTRIC", "CVD/WET", layer_hint="ILD", is_killer=True, description="层间介质层针孔漏电 (ILD Pinhole)"),
        "AZ07": DefectDefinition("AZ07", "油污油气", "COMMON", "ALL", description="真空泵油或机台导轨油气污染"),
        "AZ08": DefectDefinition("AZ08", "前制程残留", "COMMON", "ALL", description="上工序带入之残留物"),
        "AZ09": DefectDefinition("AZ09", "前制程图形缺失", "COMMON", "ALL", is_killer=True, description="下层走线断脱"),
        "AZ11": DefectDefinition("AZ11", "脏污", "COMMON", "ALL", description="环境微粒或表面附着物 (Stain)"),
        "AZ12": DefectDefinition("AZ12", "Killer", "KILLER", "ALL", is_killer=True, description="致命性不可修复缺陷 (Fatal Killer Defect)"),
        "AZ13": DefectDefinition("AZ13", "光泽Defect", "COMMON", "ALL", description="膜厚不均引发光学反射光泽差异"),
        "AZ14": DefectDefinition("AZ14", "Glass Defect", "COMMON", "ALL", description="玻璃原片母材缺陷"),
        "AZ15": DefectDefinition("AZ15", "STR水渍残", "STRIP", "WET", description="剥膜清洗后水渍残留 (Water Mark)"),
        "AZ16": DefectDefinition("AZ16", "散沙状Defect", "COMMON", "ALL", description="喷溅或微粒团聚"),
        "AZ17": DefectDefinition("AZ17", "小黑点", "COMMON", "ALL", description="微小异物颗粒"),
        "AZ18": DefectDefinition("AZ18", "其他破洞", "COMMON", "ALL", description="膜层微破洞"),
        "AZ19": DefectDefinition("AZ19", "半透明小黑点", "COMMON", "ALL", description="半透光微弱缺陷"),
        "AZ99": DefectDefinition("AZ99", "M2铝腐蚀", "CORROSION", "DET/Photo", layer_hint="M2_SourceDrain", is_killer=True, description="过孔边缘公差断裂引发含氯自催化铝腐蚀 (Al Corrosion)"),
        "0": DefectDefinition("0", "假缺陷", "FALSE_ALARM", "AOI", is_killer=False, description="AOI算法过杀识别之假缺陷"),
        "STR99": DefectDefinition("STR99", "Mark异常", "ALIGNMENT", "Photo", description="曝光对准标靶破损残缺"),
        "SDSR": DefectDefinition("SDSR", "前制程残留Short", "SHORT", "DET", is_killer=False, can_repair=True, description="金属残胶导致短路，可激光修复 (Repairable Short)"),
        "VSR_ESD": DefectDefinition("VSR_ESD", "外围静电击伤", "ESD", "ALL", is_killer=True, description="静电放电击穿烧蚀 (Electrostatic Discharge)"),
        "LSPR": DefectDefinition("LSPR", "LS PR残", "PR_RESIDUE", "Photo/ELA", layer_hint="Poly", description="准分子激光退火段残留光阻"),

        # PHT Photo / Track Specific Codes
        "P1": DefectDefinition("P1", "Coater前Particle", "PARTICLE_ZONE", "Track", description="涂胶机入口前附着颗粒"),
        "P2": DefectDefinition("P2", "Coater至显影Particle", "PARTICLE_ZONE", "Track", description="涂胶后经热板至显影段产生颗粒"),
        "P3": DefectDefinition("P3", "显影后Particle", "PARTICLE_ZONE", "Track", description="显影出板后附着颗粒"),
        "PHT01": DefectDefinition("PHT01", "Pattern上Particle", "PHOTO", "Photo", description="曝光图形内部光刻胶异物"),
        "PHT02": DefectDefinition("PHT02", "Pattern外Particle", "PHOTO", "Photo", description="曝光背景区游离异物"),
        "PHT03": DefectDefinition("PHT03", "PR残留", "PHOTO", "Photo/Track", is_killer=False, can_repair=True, description="显影不净导致光阻残留 (PR Residue)"),
        "PHT04": DefectDefinition("PHT04", "PR破洞", "PHOTO", "Photo", is_killer=True, description="光阻层破洞致使下层被误刻 (PR Pinhole)"),
        "PHT05": DefectDefinition("PHT05", "PR缺失", "PHOTO", "Photo", is_killer=True, description="光阻脱落缺失 (PR Missing)"),
        "PHT06": DefectDefinition("PHT06", "Bubble", "COATING", "Track", description="涂胶走枪起泡或显影附着气泡 (Photoresist Bubble)"),
        "PHT07": DefectDefinition("PHT07", "PR残留Short", "PHOTO", "Photo", is_killer=True, description="光阻残留桥接引发后道短路"),
        "PSE01": DefectDefinition("PSE01", "打码异常", "TITLER", "Photo", description="TT边沿标刻曝光2D码与批次序列号残缺"),
        "GTE01": DefectDefinition("GTE01", "Gate丝状残留", "RESIDUE", "Photo/DET", layer_hint="M1_Gate", description="栅极细长纤维状残胶"),
        "ILE01": DefectDefinition("ILE01", "ILD孔异常", "VIA", "Photo", layer_hint="ILD", description="介质过孔显影不良或残胶"),
        "SDE01": DefectDefinition("SDE01", "SD丝状残留", "RESIDUE", "Photo/DET", layer_hint="M2_SourceDrain", description="源漏极金属走线丝状残胶"),
        "PLE01": DefectDefinition("PLE01", "PLN孔异常", "VIA", "Photo", layer_hint="PLN", description="平坦化有机绝缘孔残胶"),
        "PLE02": DefectDefinition("PLE02", "PLN异物", "PARTICLE", "Photo", layer_hint="PLN", description="平坦化有机膜异物"),
        "DLOPEN": DefectDefinition("DLOPEN", "M2断线Defect", "OPEN", "DET/Photo", layer_hint="M2_SourceDrain", is_killer=True, description="数据线Data Line断路 (Data Line Open)"),
        "IT2CD01": DefectDefinition("IT2CD01", "ITO2 CD异常", "CD_DRIFT", "Photo/Track", layer_hint="ITO2", description="ITO2像素电极线宽均值超规格偏大漂移"),
        "PVH01": DefectDefinition("PVH01", "PV孔缺失", "VIA", "Photo", layer_hint="PV", is_killer=True, description="钝化层接触孔未开通 (Passivation Via Missing)"),

        # DET Etch & STR Strip Specific Codes
        "STR01": DefectDefinition("STR01", "Residual", "STRIP", "WET/DET", description="刻蚀或剥膜后残渣"),
        "STR02": DefectDefinition("STR02", "Short_DET", "SHORT", "DET", is_killer=True, description="刻蚀工序责任短路 (Etch-responsible Short)"),
        "STR02T": DefectDefinition("STR02T", "Short_DET可Repair", "SHORT", "DET", is_killer=False, can_repair=True, description="刻蚀责任短路 (可激光切除修复)"),
        "STR02X": DefectDefinition("STR02X", "Short_DET不可Repair", "SHORT", "DET", is_killer=True, can_repair=False, description="刻蚀责任短路 (不可修复，报废)"),
        "STR03": DefectDefinition("STR03", "图形上Particle", "PARTICLE", "WET", description="剥膜后图案上附着颗粒"),
        "STR04": DefectDefinition("STR04", "图形外Particle", "PARTICLE", "WET", description="剥膜后背景区附着颗粒"),
        "STR05": DefectDefinition("STR05", "Short_PHT", "SHORT", "Photo", is_killer=True, description="刻蚀后判定为光刻前道残胶短路 (Photo-responsible Short)"),
        "STR05T": DefectDefinition("STR05T", "Short_PHT可Repair", "SHORT", "Photo", is_killer=False, can_repair=True, description="光刻责任短路 (可激光修复)"),
        "STR05X": DefectDefinition("STR05X", "Short_PHT不可Repair", "SHORT", "Photo", is_killer=True, can_repair=False, description="光刻责任短路 (不可修复，报废)"),
        "STR06": DefectDefinition("STR06", "STR PR残", "PR_RESIDUE", "WET", description="湿法剥膜槽清洗能力衰退导致大面积残胶"),
        "STR07": DefectDefinition("STR07", "图形或线缺失", "OPEN", "DET", is_killer=True, description="金属走线过度腐蚀或断线 (Line Open)"),
        "ILS01": DefectDefinition("ILS01", "整面性过孔残留", "VIA_FAIL", "DET/WET", layer_hint="ILD", is_killer=True, description="全板面过孔内残胶未除尽"),
        "ILS02": DefectDefinition("ILS02", "单孔异常", "VIA_FAIL", "DET", layer_hint="ILD", description="孤立单一过孔接触不良"),
        "ILS03": DefectDefinition("ILS03", "多孔异常", "VIA_FAIL", "DET", layer_hint="ILD", is_killer=True, description="连续多个过孔异常"),
        "ILS04": DefectDefinition("ILS04", "ILD瞎窗", "BLIND_VIA", "DET", layer_hint="ILD", is_killer=True, description="过孔未打穿未漏底层金属 (Blind Via / Hole Block)"),
        "ILS05": DefectDefinition("ILS05", "整面性ILD过刻", "OVER_ETCH", "DET", layer_hint="ILD", is_killer=True, description="干刻各向异性失控击穿介质层"),
        "SPLASH": DefectDefinition("SPLASH", "DET静电击伤", "ESD", "DET", is_killer=True, description="刻蚀腔室异常放电或静电击伤"),
        "SPT01": DefectDefinition("SPT01", "铝咬", "CORROSION", "DET/WET", layer_hint="M2_SourceDrain", description="含氯药液横向钻掏侵蚀导致铝走线缺损发黑 (Al Bite)"),
        "SPT02": DefectDefinition("SPT02", "M3小白点", "PARTICLE", "DET", layer_hint="M3", description="后道金属表面微小白色氧化析出物"),
        "SPT03": DefectDefinition("SPT03", "圆形Splash", "SPLASH", "PVD", description="靶材溅射圆形飞溅点"),

        # CVD / PVD / ELA / RTA Codes
        "CVD01": DefectDefinition("CVD01", "CVD膜上Particle", "PARTICLE", "CVD", description="化学气相沉积膜上微粒"),
        "CVD02": DefectDefinition("CVD02", "CVD膜内Particle", "PARTICLE", "CVD", description="化学气相沉积包覆内部微粒"),
        "CVD03": DefectDefinition("CVD03", "CVD Splash", "SPLASH", "CVD", description="反应气体聚合飞溅物"),
        "CVD05": DefectDefinition("CVD05", "CVD Peeling", "PEELING", "CVD", is_killer=True, description="绝缘层应力失衡脱落剥离 (Peeling)"),
        "PL01": DefectDefinition("PL01", "黑色异物", "FOREIGN_MATTER", "CVD", description="深色有机碳化异物"),
        "PL02": DefectDefinition("PL02", "黄色异物", "FOREIGN_MATTER", "CVD", description="胶质或聚合物变色异物"),
        "PVD01": DefectDefinition("PVD01", "PVD膜上Particle", "PARTICLE", "PVD", description="物理气相沉积表面微粒"),
        "PVD02": DefectDefinition("PVD02", "PVD膜内Particle", "PARTICLE", "PVD", description="物理气相沉积夹层内部微粒"),
        "PVD03": DefectDefinition("PVD03", "PVD大型Particle", "PARTICLE", "PVD", is_killer=True, description="靶材脱落产生之巨型微粒"),
        "PVD04": DefectDefinition("PVD04", "PVD Peeling", "PEELING", "PVD", is_killer=True, description="金属膜层附着力不良脱膜"),
        "PVD05": DefectDefinition("PVD05", "PVD Splash", "SPLASH", "PVD", description="磁控溅射靶材微爆飞溅 (Sputter Splash)"),
        "PVD07": DefectDefinition("PVD07", "异常放电", "ARCING", "PVD", description="腔体电弧异常打火 (Target Arcing)"),
        "PVD08": DefectDefinition("PVD08", "M2异物", "PARTICLE", "PVD", layer_hint="M2_SourceDrain", description="源漏极金属层夹带异物"),
        "PSL01": DefectDefinition("PSL01", "ELA膜上Particle", "PARTICLE", "ELA", layer_hint="Poly", description="激光退火表面颗粒"),
        "PSL03": DefectDefinition("PSL03", "麻点", "SURFACE", "ELA", layer_hint="Poly", description="多晶硅结晶微观麻点 (Pit)"),
        "PSL05": DefectDefinition("PSL05", "爆状Defect", "DAMAGE", "ELA", layer_hint="Poly", is_killer=True, description="准分子激光局部能量密度超标炸裂"),
        "ILR01": DefectDefinition("ILR01", "ILD膜下异物", "FOREIGN_MATTER", "RTA", layer_hint="ILD", description="快速热退火介质层下包埋异物"),
        "ILR07": DefectDefinition("ILR07", "彩色环状", "MURA", "RTA", description="膜厚不均引发光学干涉彩环 (Color Ring)"),
        "MoPP": DefectDefinition("MoPP", "Mo Pad Peeling", "PEELING", "DET", layer_hint="M1_Gate", is_killer=True, description="钼金属接触垫剥落脱扣"),

        # ITO & Passivation Codes
        "ITE01": DefectDefinition("ITE01", "ITO1过刻", "OVER_ETCH", "DET/WET", layer_hint="ITO1", description="底层像素电极过度侵蚀"),
        "ITE02": DefectDefinition("ITE02", "ITO2缺失", "OPEN", "DET/WET", layer_hint="ITO2", is_killer=True, description="顶层ITO像素电极图形断缺"),
        "ITE02X": DefectDefinition("ITE02X", "ITO2缺失锯齿状", "OPEN", "DET/WET", layer_hint="ITO2", is_killer=True, description="光阻粘附不良导致ITO2呈锯齿状破损脱落"),
        "ITE03": DefectDefinition("ITE03", "ITO2残留", "RESIDUE", "WET", layer_hint="ITO2", description="像素电极刻蚀不尽桥接"),
        "PVP01": DefectDefinition("PVP01", "PV Peeling", "PEELING", "WET/CVD", layer_hint="PV", is_killer=True, description="保护钝化层破损剥离"),
        "PVB01": DefectDefinition("PVB01", "PV Bubble", "BUBBLE", "Track/CVD", layer_hint="PV", description="钝化层内部微小起泡"),
        "PADP": DefectDefinition("PADP", "外围电路Peeling", "PEELING", "WET", description="走线引脚Pad区金属剥离"),
        "M3EMT": DefectDefinition("M3EMT", "M3线发亮", "OPTICAL", "AOI", layer_hint="M3", description="第三层金属走线反光异常"),
    }

    # 4. Standard 5-digit Operation Station Codes Catalog (*103 = Depo AOI, *303 = PH ADI, *603 = ET/STR AEI)
    OPERATION_CATALOG: Dict[str, OperationStation] = {
        "10113": OperationStation("10113", "SHIELD DEPO ADI", "SHIELD", "DEPO_AOI"),
        "10300": OperationStation("10300", "SHIELD PH TRACK/EXP", "SHIELD", "PH_PROC"),
        "10303": OperationStation("10303", "SHIELD PH AOI", "SHIELD", "PH_ADI"),
        "10500": OperationStation("10500", "SHIELD DET", "SHIELD", "ET_PROC"),
        "10603": OperationStation("10603", "SHIELD ET AEI", "SHIELD", "ET_AEI"),
        "11103": OperationStation("11103", "3LAYER DEPO ADI", "POLY_CVD", "DEPO_AOI"),
        "11200": OperationStation("11200", "ELA EXCIMER ANNEAL", "POLY", "ANNEAL_PROC"),
        "11203": OperationStation("11203", "ELA AOI", "POLY", "ANNEAL_AOI"),
        "11300": OperationStation("11300", "POLY PH TRACK/EXP", "POLY", "PH_PROC"),
        "11303": OperationStation("11303", "POLY PH AOI", "POLY", "PH_ADI"),
        "11600": OperationStation("11600", "POLY ET / STR", "POLY", "ET_PROC"),
        "11603": OperationStation("11603", "POLY ET AEI", "POLY", "ET_AEI"),
        "12300": OperationStation("12300", "CHD PH", "CHD", "PH_PROC"),
        "12303": OperationStation("12303", "CHD PH AOI", "CHD", "PH_ADI"),
        "12603": OperationStation("12603", "CHD STR AEI", "CHD", "ET_AEI"),
        "13300": OperationStation("13300", "ND PH", "ND", "PH_PROC"),
        "13303": OperationStation("13303", "ND PH ADI", "ND", "PH_ADI"),
        "13603": OperationStation("13603", "ND STR AEI", "ND", "ET_AEI"),
        "14103": OperationStation("14103", "GI DEPO ADI", "GI", "DEPO_AOI"),
        "14203": OperationStation("14203", "GATE DEPO ADI", "M1_GATE", "DEPO_AOI"),
        "14300": OperationStation("14300", "GATE PH TRACK/EXP", "M1_GATE", "PH_PROC"),
        "14303": OperationStation("14303", "GATE PH AOI", "M1_GATE", "PH_ADI"),
        "14500": OperationStation("14500", "GATE DET ETCH", "M1_GATE", "ET_PROC"),
        "14603": OperationStation("14603", "GATE ET AEI", "M1_GATE", "ET_AEI"),
        "15300": OperationStation("15300", "PD PH", "PD", "PH_PROC"),
        "15303": OperationStation("15303", "PD PH ADI", "PD", "PH_ADI"),
        "15500": OperationStation("15500", "PD ASHING", "PD", "ASHING"),
        "15603": OperationStation("15603", "PD STR AOI", "PD", "ET_AEI"),
        "16103": OperationStation("16103", "ILD DEPO ADI", "ILD", "DEPO_AOI"),
        "16203": OperationStation("16203", "ILD RTA AEI", "ILD", "ANNEAL_AOI"),
        "16300": OperationStation("16300", "ILD PH TRACK/EXP", "ILD", "PH_PROC"),
        "16303": OperationStation("16303", "ILD PH AOI", "ILD", "PH_ADI"),
        "16500": OperationStation("16500", "ILD DET ETCH", "ILD", "ET_PROC"),
        "16603": OperationStation("16603", "ILD ET AEI", "ILD", "ET_AEI"),
        "17103": OperationStation("17103", "SD DEPO ADI", "M2_SD", "DEPO_AOI"),
        "17300": OperationStation("17300", "SD PH TRACK/EXP", "M2_SD", "PH_PROC"),
        "17303": OperationStation("17303", "SD PH AOI", "M2_SD", "PH_ADI"),
        "17500": OperationStation("17500", "SD DET ETCH", "M2_SD", "ET_PROC"),
        "17603": OperationStation("17603", "SD ET AEI", "M2_SD", "ET_AEI"),
        "18300": OperationStation("18300", "PLN PH TRACK", "PLN", "PH_PROC"),
        "18303": OperationStation("18303", "PLN PH AOI", "PLN", "PH_ADI"),
        "19103": OperationStation("19103", "ITO1 DEPO ADI", "ITO1", "DEPO_AOI"),
        "19300": OperationStation("19300", "ITO1 PH", "ITO1", "PH_PROC"),
        "19303": OperationStation("19303", "ITO1 PH AOI", "ITO1", "PH_ADI"),
        "19500": OperationStation("19500", "ITO1 WET ETCH", "ITO1", "ET_PROC"),
        "19603": OperationStation("19603", "ITO1 ET AEI", "ITO1", "ET_AEI"),
        "1A103": OperationStation("1A103", "PAS DEPO AOI", "PAS", "DEPO_AOI"),
        "1A300": OperationStation("1A300", "PV/PAS PH", "PV", "PH_PROC"),
        "1A303": OperationStation("1A303", "PV PH AOI", "PV", "PH_ADI"),
        "1A500": OperationStation("1A500", "PV ETCH", "PV", "ET_PROC"),
        "1A603": OperationStation("1A603", "PAS ET AEI", "PAS", "ET_AEI"),
        "1B103": OperationStation("1B103", "ITO2 DEPO ADI", "ITO2", "DEPO_AOI"),
        "1B300": OperationStation("1B300", "ITO2 PH", "ITO2", "PH_PROC"),
        "1B303": OperationStation("1B303", "ITO2 PH AOI", "ITO2", "PH_ADI"),
        "1B500": OperationStation("1B500", "ITO2 WET ETCH", "ITO2", "ET_PROC"),
        "1B603": OperationStation("1B603", "ITO2 ET AEI", "ITO2", "ET_AEI"),
        "1B700": OperationStation("1B700", "ITO ANNEAL", "ITO2", "ANNEAL_PROC"),
        "1B703": OperationStation("1B703", "FINAL AOI", "FINAL", "FINAL_AOI"),
        "1E103": OperationStation("1E103", "M3 DEPO ADI", "M3", "DEPO_AOI"),
        "1E303": OperationStation("1E303", "M3 PHT AOI", "M3", "PH_ADI"),
        "1E603": OperationStation("1E603", "M3 ET AEI", "M3", "ET_AEI"),
    }

    # 5. Equipment Model & Vendor Catalog (Extracted from G6 configuration & Onboarding Exams)
    EQUIPMENT_TYPES = {
        "PHT": "黄光涂胶显影机 (Track: TEL Exceliner / DNS)",
        "EXP": "曝光机 (Stepper/Scanner: Nikon / Canon MPAsp-E813P)",
        "AOI": "自动光学检查机 (AOI 100~800: 澳宝 Orbotech / Toray)",
        "DET": "干法刻蚀机 (Dry Etcher: TEL / ICP / RIE)",
        "WET": "湿法刻蚀剥膜机 (Wet Bench / Batch Strip)",
        "STR": "剥膜机 (Strip Wet Station: STR100~STR800)",
        "CVD": "等离子体化学气相沉积机 (PECVD: AKT / Ulvac)",
        "PVD": "磁控溅射镀膜机 (Sputter: AKT / Ulvac)",
        "ELA": "准分子激光退火机 (JSW / Coherent)",
        "CDC": "线宽测量显微镜 (Critical Dimension Measurement: CD-SEM / Optical CDC)",
        "MAC": "套刻对准测量机 (Macro/Micro Alignment Check / Overlay)",
        "TCU": "曝光温控单元 (Temperature Control Unit)",
        "TT": "标刻打码机 (Titler: EO Technics LTE-5500RC)",
        "EE": "边沿曝光机 (Edge Exposure)",
        "Hosan": "化学品供应与混配柜 (Hosan Chemical Dispense System)",
    }

    DEFECT_CODE_REGEX = re.compile(
        r"\b(?:AZ(?:0[1-9]|1[0-9]|99)|P[1-3]|PHT0[1-7]|STR0[1-7][TX]?|CVD0[1-5]|PVD0[1-8]|"
        r"PSL0[1-5]|ILR0[1-8]|ILS0[1-5]|ITE0[1-3]X?|IT2CD01|DLOPEN|MoPP|SPLASH|SPT0[1-3]|"
        r"PVH01|PVP01|PVB01|GTE01|SDE01|ILE01|PLE0[1-2]|PSE01|PADP|M3EMT|SDSR|LSPR)\b",
        re.IGNORECASE
    )

    OPERATION_CODE_REGEX = re.compile(
        r"\b(?:10113|10300|10303|10500|10603|11103|11200|11203|11300|11303|11600|11603|"
        r"12300|12303|12603|13300|13303|13603|14103|14203|14300|14303|14500|14603|"
        r"15300|15303|15500|15603|16103|16203|16300|16303|16500|16603|17103|17300|"
        r"17303|17500|17603|18300|18303|19103|19300|19303|19500|19603|1A103|1A300|"
        r"1A303|1A500|1A603|1B103|1B300|1B303|1B500|1B603|1B700|1B703|1E103|1E303|1E603)\b"
    )

    MACHINE_ID_REGEX = re.compile(
        r"\b[AFCM]1(?:PHT|AOI|CVD|PVD|DET|STR|CDC|MAC|ELA|ICL|PDC|RSM|IMP|PIL|RUB|ODF|SSL|SLM|SPT|MIC|WET|PRR|REP)\d{3}\b"
    )

    @classmethod
    def lookup_defect(cls, code: str) -> Optional[DefectDefinition]:
        return cls.DEFECT_CATALOG.get(code.upper())

    @classmethod
    def lookup_operation(cls, op_code: str) -> Optional[OperationStation]:
        return cls.OPERATION_CATALOG.get(op_code.upper())

    @classmethod
    def scan_text(cls, text: str) -> Dict[str, Any]:
        if not text:
            return {"defects": [], "operations": [], "machines": [], "summary_zh": ""}

        raw_defects = list(set(cls.DEFECT_CODE_REGEX.findall(text)))
        raw_ops = list(set(cls.OPERATION_CODE_REGEX.findall(text)))
        raw_eqs = list(set(cls.MACHINE_ID_REGEX.findall(text)))

        resolved_defects = []
        for d in raw_defects:
            df = cls.lookup_defect(d)
            if df:
                resolved_defects.append({
                    "code": df.code,
                    "name": df.name_zh,
                    "category": df.category,
                    "station": df.station_default,
                    "layer": df.layer_hint,
                    "is_killer": df.is_killer,
                    "description": df.description
                })

        resolved_ops = []
        for op in raw_ops:
            station = cls.lookup_operation(op)
            if station:
                resolved_ops.append({
                    "op_code": station.op_code,
                    "name": station.name,
                    "layer": station.layer,
                    "step_type": station.step_type
                })

        summary_parts = []
        if resolved_defects:
            def_names = [f"{d['code']}({d['name']})" for d in resolved_defects]
            summary_parts.append(f"检出缺陷: {', '.join(def_names)}")
        if resolved_ops:
            op_names = [f"{op['op_code']}({op['name']})" for op in resolved_ops]
            summary_parts.append(f"涉及站点: {', '.join(op_names)}")
        if raw_eqs:
            summary_parts.append(f"涉及机台: {', '.join(sorted(raw_eqs))}")

        return {
            "defects": resolved_defects,
            "operations": resolved_ops,
            "machines": sorted(raw_eqs),
            "summary_zh": " | ".join(summary_parts)
        }
