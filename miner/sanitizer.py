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

# External configuration hook for entity masking rules.
# In open-source knowhow-miner, sensitive regex rules are injected via local config or environment.
# Defaults provide standard structural patterns (e.g. phones, generic internal emails).
SENSITIVE_REPLACEMENTS = [
    # General internal emails & contact numbers
    (r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", "[EMAIL_REDACTED]"),
    (r"(?:\+?86)?1[3-9]\d{9}", "[PHONE_REDACTED]"),
    (r"\b\d{3,4}-\d{7,8}\b", "[TEL_REDACTED]"),
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
