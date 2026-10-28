import re
import email.utils
from datetime import datetime
from typing import List, Optional, Set, Dict, Any
from dataclasses import dataclass, field

@dataclass
class CleanedEmail:
    msg_id: str
    in_reply_to: Optional[str]
    references: List[str]
    date_str: str
    timestamp: float
    from_addr: str
    to_addrs: List[str]
    cc_addrs: List[str]
    subject: str
    normalized_subject: str
    body_clean: str
    attachments: List[str]
    source_mbox: str
    seq_num: int
    entities: Dict[str, List[str]] = field(default_factory=dict)

class EmailCleaner:
    # Notice / Disclaimer patterns
    LEGAL_DISCLAIMER_PATTERNS = [
        r"This e-mail message together with any attachments.*",
        r"本电子邮件及附件（如有）所载信息均为保密信息.*",
        r"本邮件及其附件包含机密信息.*",
        r"本信息属于企业机密.*",
        r"未经授权者收到此信息均无权阅读.*",
        r"Confidentiality Notice:.*",
        r"CONFIDENTIALITY NOTICE:.*",
        r"\*\*\* DISCLAIMER \*\*\*.*",
        r"This email transmission may contain confidential.*",
        r"Any unauthorized dissemination is strictly prohibited.*",
        r"此邮件为系统自动发出，请勿回复.*"
    ]
    
    # Anonymization Patterns (Generic fab blacklist)
    EMAIL_ADDR_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
    PHONE_REGEX = re.compile(r"\b(?:\+?86[- ]?)?1[3-9]\d{9}\b")
    CORP_DOMAIN_REGEX = re.compile(r"[a-zA-Z0-9-]+\.(?:cn|com|com\.cn)", re.IGNORECASE)
    CORP_NAME_REGEX = re.compile(r"(?:[A-Z0-9a-z\u4e00-\u9fa5]{2,6}(?:微电子|光电|医疗|重工|科技|半导体|面板厂|产业基地))", re.IGNORECASE)

    @classmethod
    def anonymize_text(cls, text: str) -> str:
        """
        Strips private corporate names, personal phones, emails, and employee IDs.
        """
        if not text:
            return ""
        # 1. Replace emails with role tags
        text = cls.EMAIL_ADDR_REGEX.sub("[ENGINEER_EMAIL]", text)
        # 2. Replace phones
        text = cls.PHONE_REGEX.sub("[PHONE_REDACTED]", text)
        # 3. Replace company domains & names
        text = cls.CORP_NAME_REGEX.sub("[FPD_FAB]", text)
        return text
    
    # Subject normalization prefixes
    SUBJECT_PREFIX_REGEX = re.compile(
        r"^(?:(?:re|fwd|fw|答复|回复|转发)\s*[:：]\s*)+", 
        re.IGNORECASE
    )
    
    # Entity extraction patterns (Lot ID, Glass ID, Defect Code, Machine/Chamber)
    LOT_ID_REGEX = re.compile(r"\b[A-Z0-9]{2}[0-9A-Z]{2}[A-Z]{2}[0-9]{3,4}\b")
    GLASS_ID_REGEX = re.compile(r"\b[0-9A-Z]{4,5}[0-9A-Z]{5,8}\b")
    DEFECT_CODE_REGEX = re.compile(r"\b(?:AZ[0-9]{2,3}|D-[A-Za-z0-9]+|Mura|Open|Short|Bridge)\b", re.IGNORECASE)
    CHAMBER_REGEX = re.compile(r"\b(?:PHT[0-9A-Za-z]{3,4}|DETA[0-9A-Za-z]{2,3}|CVD[0-9A-Za-z]{2,3}|PVD[0-9A-Za-z]{2,3}|HP[0-9]{1,2})\b")
    PRODUCT_REGEX = re.compile(r"\b(?:[4-9]\.[0-9]{2}(?:FHD|WQ|TED|NMOS)?|TED|Incell|In-cell)\b", re.IGNORECASE)

    @classmethod
    def clean_subject(cls, subject: str) -> str:
        if not subject:
            return ""
        # Strip repeated Re:/Fwd:/答复:
        norm = cls.SUBJECT_PREFIX_REGEX.sub("", subject.strip()).strip()
        # Anonymize
        norm = cls.anonymize_text(norm)
        # Clean extra whitespace
        return " ".join(norm.split())

    PHONE_SIGNATURE_REGEX = re.compile(r"(?:Tel|Mobile|Phone|电话|手机|分机)\s*[:：]\s*[0-9-+\s]{5,20}", re.IGNORECASE)
    OFFICE_REGEX = re.compile(r"(?:Office|工位|分机号)\s*[:：]\s*[A-Za-z0-9-]+", re.IGNORECASE)
    THREAD_QUOTE_SPLITTERS = [
        re.compile(r"^-+\s*(?:Original Message|原始邮件)\s*-+", re.IGNORECASE | re.MULTILINE),
        re.compile(r"^_{20,}", re.MULTILINE),
        re.compile(r"^On\s+.*?\s+wrote:\s*$", re.IGNORECASE | re.MULTILINE)
    ]

    @classmethod
    def extract_delta_body(cls, text: str) -> str:
        """
        Extracts only the latest message increment, cutting off historical reply chains.
        """
        if not text:
            return ""
        for splitter in cls.THREAD_QUOTE_SPLITTERS:
            parts = splitter.split(text, maxsplit=1)
            if len(parts) > 1:
                text = parts[0]
        return text

    @classmethod
    def clean_body(cls, text: str, extract_delta: bool = False) -> str:
        if not text:
            return ""
        if extract_delta:
            text = cls.extract_delta_body(text)

        # 1. Remove legal disclaimers
        for pat in cls.LEGAL_DISCLAIMER_PATTERNS:
            text = re.sub(pat, " ", text, flags=re.DOTALL | re.IGNORECASE)
            
        # 2. Strip phone & office noise from signatures
        text = cls.PHONE_SIGNATURE_REGEX.sub(" ", text)
        text = cls.OFFICE_REGEX.sub(" ", text)

        # 3. Split lines and strip quote headers
        lines = text.splitlines()
        clean_lines = []
        for line in lines:
            line_str = line.strip()
            if line_str.startswith(">"):
                continue
            if line_str.startswith("-----原始邮件-----") or line_str.startswith("----- Original Message -----") or line_str.startswith("________________________________"):
                continue
            clean_lines.append(line_str)
            
        full_text = "\n".join(clean_lines)
        # Anonymize
        full_text = cls.anonymize_text(full_text)
        # Normalize multiple spaces / newlines
        full_text = re.sub(r"\n{3,}", "\n\n", full_text).strip()
        return full_text

    @classmethod
    def parse_timestamp(cls, date_str: str) -> float:
        if not date_str:
            return 0.0
        try:
            parsed = email.utils.parsedate_to_datetime(date_str)
            return parsed.timestamp()
        except Exception:
            return 0.0

    @classmethod
    def extract_entities(cls, text: str, subject: str) -> Dict[str, List[str]]:
        combined = f"{subject} \n {text}"
        entities = {
            "lots": sorted(list(set(cls.LOT_ID_REGEX.findall(combined)))),
            "chambers": sorted(list(set(cls.CHAMBER_REGEX.findall(combined)))),
            "defect_codes": sorted(list(set(cls.DEFECT_CODE_REGEX.findall(combined)))),
            "products": sorted(list(set(cls.PRODUCT_REGEX.findall(combined))))
        }
        return entities
