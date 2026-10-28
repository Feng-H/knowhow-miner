import os
import re
import zipfile
from typing import List, Dict, Any, Optional

try:
    import xlrd
except ImportError:
    xlrd = None

class ExcelSplitTableParser:
    """
    Extracts DOE split conditions, POR baseline, and experimental slots from .xlsx and .xls files.
    """

    HEADER_KEYWORDS = [
        "slot", "lot", "glass", "recipe", "condition", "dose", "focus",
        "cd", "yield", "良率", "膜厚", "条件", "工步", "机台"
    ]

    @classmethod
    def parse(cls, file_path: str) -> Dict[str, Any]:
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}", "sheets": []}

        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".xlsx":
            return cls._parse_xlsx(file_path)
        elif ext == ".xls":
            return cls._parse_xls(file_path)
        else:
            return {"error": f"Unsupported format: {ext}", "sheets": []}

    @classmethod
    def _parse_xlsx(cls, file_path: str) -> Dict[str, Any]:
        sheets_data = []
        try:
            with zipfile.ZipFile(file_path) as z:
                # 1. Read shared strings
                shared_strings = []
                if "xl/sharedStrings.xml" in z.namelist():
                    ss_xml = z.read("xl/sharedStrings.xml").decode("utf-8", errors="ignore")
                    shared_strings = re.findall(r"<t(?: [^>]*)?>(.*?)</t>", ss_xml, flags=re.DOTALL)

                # 2. Read sheets
                sheet_files = [f for f in z.namelist() if f.startswith("xl/worksheets/sheet") and f.endswith(".xml")]
                sheet_files.sort()

                for s_file in sheet_files:
                    s_xml = z.read(s_file).decode("utf-8", errors="ignore")
                    rows_xml = re.findall(r"<row[^>]*>(.*?)</row>", s_xml, flags=re.DOTALL)
                    
                    parsed_rows = []
                    for r_xml in rows_xml:
                        cells = re.findall(r'<c [^>]*t="s"[^>]*><v>(\d+)</v></c>|<c [^>]*><v>([^<]+)</v></c>', r_xml)
                        row_vals = []
                        for s_idx, direct_val in cells:
                            if s_idx and int(s_idx) < len(shared_strings):
                                row_vals.append(shared_strings[int(s_idx)].strip())
                            elif direct_val:
                                row_vals.append(direct_val.strip())
                            else:
                                row_vals.append("")
                        if any(row_vals):
                            parsed_rows.append(row_vals)

                    # Identify Split Table
                    split_table = cls._detect_split_table(parsed_rows)
                    sheets_data.append({
                        "sheet_name": os.path.basename(s_file),
                        "total_rows": len(parsed_rows),
                        "split_table": split_table
                    })

            return {
                "file_path": file_path,
                "format": "xlsx",
                "sheets": sheets_data
            }
        except Exception as e:
            return {"file_path": file_path, "format": "xlsx", "error": str(e), "sheets": []}

    @classmethod
    def _parse_xls(cls, file_path: str) -> Dict[str, Any]:
        if xlrd is None:
            return {"file_path": file_path, "format": "xls", "error": "xlrd not installed", "sheets": []}
        try:
            wb = xlrd.open_workbook(file_path)
            sheets_data = []
            for sheet_name in wb.sheet_names():
                sh = wb.sheet_by_name(sheet_name)
                parsed_rows = []
                for r in range(sh.nrows):
                    row_vals = [str(sh.cell_value(r, c)).strip() for c in range(sh.ncols)]
                    if any(row_vals):
                        parsed_rows.append(row_vals)

                split_table = cls._detect_split_table(parsed_rows)
                sheets_data.append({
                    "sheet_name": sheet_name,
                    "total_rows": len(parsed_rows),
                    "split_table": split_table
                })

            return {
                "file_path": file_path,
                "format": "xls",
                "sheets": sheets_data
            }
        except Exception as e:
            return {"file_path": file_path, "format": "xls", "error": str(e), "sheets": []}

    @classmethod
    def _detect_split_table(cls, rows: List[List[str]]) -> Optional[Dict[str, Any]]:
        """
        Detects header row and groups slots into POR baseline vs Experimental splits.
        """
        header_idx = -1
        header_row = []

        for idx, row in enumerate(rows[:25]):
            matched = sum(1 for cell in row if any(kw in cell.lower() for kw in cls.HEADER_KEYWORDS))
            if matched >= 3:
                header_idx = idx
                header_row = [c.lower() for c in row]
                break

        if header_idx == -1:
            return None

        # Extract rows under header
        split_slots = []
        por_slots = []

        for r in rows[header_idx + 1:]:
            row_str = " ".join(r).lower()
            if not row_str.strip():
                continue
            
            is_por = any(p in row_str for p in ["por", "standard", "baseline", "标准"])
            entry = {f"col_{i}": val for i, val in enumerate(r) if val}
            if is_por:
                por_slots.append(entry)
            else:
                split_slots.append(entry)

        return {
            "header": header_row,
            "por_count": len(por_slots),
            "split_count": len(split_slots),
            "por_sample": por_slots[:3],
            "split_sample": split_slots[:5]
        }
