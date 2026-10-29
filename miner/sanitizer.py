"""
PII & Corporate Entity Sanitizer
================================
Author: John Huang & Hermes Agent
License: CC BY-NC-SA 4.0 (Creative Commons Attribution-NonCommercial-ShareAlike 4.0)

Ensures all query outputs returned from the L1 KnowledgeStore or MCP endpoints are strictly
sanitized of corporate names, personal names, phone numbers, and internal emails.
"""

import re
from typing import Dict, Any, List

# Entity Masking Patterns
SENSITIVE_REPLACEMENTS = [
    # Corporate & Fab Names
    (r"(厦门天马|天马微电子|天马|Tianma|TM)", "国内某头部G6 LTPS产线"),
    (r"(华星光电|华星|CSOT|T1|T2|华星T1|华星T2)", "某头部G8.5阵列厂"),
    (r"(微智医疗|微智|Intellimicro)", "某微电子芯片制造基地"),
    
    # Internal emails
    (r"[a-zA-Z0-9_.+-]+@(tianma|csot|intellimicro|foxmail)\.[a-zA-Z0-9-.]+", "[EMAIL_REDACTED]"),
    
    # Chinese Phone Numbers
    (r"(?:\+?86)?1[3-9]\d{9}", "[PHONE_REDACTED]"),
    (r"\b\d{3,4}-\d{7,8}\b", "[TEL_REDACTED]"),
    
    # Internal Person names (known leads & engineers)
    (r"黄祥发", "光刻主管工程师"),
    (r"黄峰", "资深黄光工艺工程师"),
    (r"王秀丽", "刻蚀主管工程师"),
    (r"靳海仲", "湿法主管工程师"),
    (r"沈心睿", "CVD薄膜主管工程师"),
    (r"赵春凤", "PVD薄膜主管工程师"),
    (r"王玲", "ELA激光退火主管"),
    (r"顾寒昱", "PI制程整合主管"),
    (r"姜文鑫", "RD版图研发主管"),
    (r"许津榕", "厂务调度工程师"),
    (r"廖智宏", "Array技术主管"),
]

def sanitize_text(text: str) -> str:
    """
    Scans and replaces sensitive personal, contact, and fab entities with generic engineering roles.
    """
    if not text:
        return ""
    result = str(text)
    for pattern, replacement in SENSITIVE_REPLACEMENTS:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    return result

def sanitize_crystal_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep sanitizes an L1 crystal record before sending it across the public web API or MCP.
    """
    if not record:
        return {}
    
    sanitized = {}
    for k, v in record.items():
        if isinstance(v, str):
            sanitized[k] = sanitize_text(v)
        elif isinstance(v, list):
            sanitized[k] = [
                sanitize_crystal_record(item) if isinstance(item, dict)
                else (sanitize_text(item) if isinstance(item, str) else item)
                for item in v
            ]
        elif isinstance(v, dict):
            sanitized[k] = sanitize_crystal_record(v)
        else:
            sanitized[k] = v
            
    # Never leak raw message IDs or internal tracking IDs
    if "evidence_anchor" in sanitized:
        anchors = sanitized["evidence_anchor"]
        if isinstance(anchors, list):
            for a in anchors:
                if isinstance(a, dict) and "message_id" in a:
                    a["message_id"] = "[VERIFIED_INTERNAL_ID]"
                    
    return sanitized
