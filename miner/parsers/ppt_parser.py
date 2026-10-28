import os
import re
import zipfile
import struct
from typing import List, Dict, Any, Optional

try:
    import olefile
except ImportError:
    olefile = None

class PPTDeepParser:
    """
    Extracts text, slide structure, tables, and 5-Why/cause sections from .pptx and .ppt files.
    """

    KEYWORD_PATTERNS = [
        r"原因", r"机理", r"5-Why", r"5Why", r"对策", r"改善", r"参数", r"对比",
        r"DOE", r"良率", r"结论", r"真因", r"异常", r"CD", r"Taper", r"Mura", r"腐蚀"
    ]

    @classmethod
    def parse(cls, file_path: str) -> Dict[str, Any]:
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}", "slides": []}

        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".pptx":
            return cls._parse_pptx(file_path)
        elif ext == ".ppt":
            return cls._parse_ppt(file_path)
        else:
            return {"error": f"Unsupported format: {ext}", "slides": []}

    @classmethod
    def _parse_pptx(cls, file_path: str) -> Dict[str, Any]:
        slides_data = []
        try:
            with zipfile.ZipFile(file_path) as z:
                slide_names = [f for f in z.namelist() if f.startswith("ppt/slides/slide") and f.endswith(".xml")]
                def _get_slide_num(s: str) -> int:
                    m = re.search(r"slide(\d+)\.xml", s)
                    return int(m.group(1)) if m else 9999

                slide_names.sort(key=_get_slide_num)

                for idx, s_name in enumerate(slide_names):
                    content = z.read(s_name).decode("utf-8", errors="ignore")
                    # Extract text between <a:t>...</a:t>
                    text_pieces = re.findall(r"<a:t>(.*?)</a:t>", content, flags=re.DOTALL)
                    clean_text = " ".join([t.strip() for t in text_pieces if t.strip()])
                    
                    # Highlight keywords
                    matched_kws = [kw for kw in cls.KEYWORD_PATTERNS if re.search(kw, clean_text, re.IGNORECASE)]

                    slides_data.append({
                        "slide_index": idx + 1,
                        "text": clean_text,
                        "keywords": matched_kws,
                        "is_critical": len(matched_kws) >= 2
                    })

            return {
                "file_path": file_path,
                "format": "pptx",
                "total_slides": len(slides_data),
                "slides": slides_data
            }
        except Exception as e:
            return {"file_path": file_path, "format": "pptx", "error": str(e), "slides": []}

    @classmethod
    def _parse_ppt(cls, file_path: str) -> Dict[str, Any]:
        """
        Parses binary legacy PPT using OLE text atom parsing with fallback carving.
        """
        slides_data = []
        if olefile is None:
            return {"file_path": file_path, "format": "ppt", "error": "olefile library missing", "slides": []}

        try:
            if not olefile.isOleFile(file_path):
                # Try fallback zip carving
                return cls._carve_embedded_zip(file_path)

            ole = olefile.OleFileIO(file_path)
            if not ole.exists("PowerPoint Document"):
                return {"file_path": file_path, "format": "ppt", "error": "No PowerPoint Document stream", "slides": []}

            data = ole.openstream("PowerPoint Document").read()
            texts = cls._extract_ppt_records(data)

            # Cluster texts into pseudo-slides based on slide headers
            current_slide = []
            slide_idx = 1
            for t in texts:
                current_slide.append(t)
                if len(current_slide) >= 6 or any(h in t for h in ["5-Why", "5Why", "调查", "总结", "对策"]):
                    slide_text = " \n ".join(current_slide)
                    matched_kws = [kw for kw in cls.KEYWORD_PATTERNS if re.search(kw, slide_text, re.IGNORECASE)]
                    slides_data.append({
                        "slide_index": slide_idx,
                        "text": slide_text,
                        "keywords": matched_kws,
                        "is_critical": len(matched_kws) >= 2
                    })
                    slide_idx += 1
                    current_slide = []

            if current_slide:
                slide_text = " \n ".join(current_slide)
                matched_kws = [kw for kw in cls.KEYWORD_PATTERNS if re.search(kw, slide_text, re.IGNORECASE)]
                slides_data.append({
                    "slide_index": slide_idx,
                    "text": slide_text,
                    "keywords": matched_kws,
                    "is_critical": len(matched_kws) >= 2
                })

            return {
                "file_path": file_path,
                "format": "ppt",
                "total_slides": len(slides_data),
                "slides": slides_data
            }
        except Exception as e:
            return cls._carve_embedded_zip(file_path)

    @classmethod
    def _extract_ppt_records(cls, data: bytes, offset: int = 0, end: Optional[int] = None) -> List[str]:
        if end is None:
            end = len(data)
        pos = offset
        texts = []
        while pos < end - 8:
            ver_inst, rec_type, rec_len = struct.unpack("<HHI", data[pos:pos+8])
            rec_ver = ver_inst & 0x0F
            content_pos = pos + 8
            next_pos = content_pos + rec_len
            if next_pos > end:
                break

            if rec_type in [4008, 0x0FA8]:  # TextCharsAtom (UTF-16LE)
                try:
                    t = data[content_pos:next_pos].decode("utf-16le").strip()
                    if t and len(t) > 2:
                        texts.append(t)
                except Exception:
                    pass
            elif rec_type in [4000, 0x0FA0]:  # TextBytesAtom (ANSI/GB18030)
                try:
                    t = data[content_pos:next_pos].decode("gb18030", errors="ignore").strip()
                    if t and len(t) > 2:
                        texts.append(t)
                except Exception:
                    pass
            elif rec_ver == 0x0F:  # Container
                texts.extend(cls._extract_ppt_records(data, content_pos, next_pos))

            pos = next_pos
        return texts

    @classmethod
    def _carve_embedded_zip(cls, file_path: str) -> Dict[str, Any]:
        """Fallback for PPT files that wrap an internal ZIP/PPTX container."""
        try:
            with open(file_path, "rb") as f:
                data = f.read()
            pk_pos = data.find(b"PK\x03\x04")
            if pk_pos != -1:
                import io
                zip_data = data[pk_pos:]
                with zipfile.ZipFile(io.BytesIO(zip_data)) as z:
                    slide_names = [s for s in z.namelist() if "slide" in s and s.endswith(".xml")]
                    slides = []
                    for idx, s_name in enumerate(sorted(slide_names)):
                        c = z.read(s_name).decode("utf-8", errors="ignore")
                        text_pieces = re.findall(r"<a:t>(.*?)</a:t>", c, flags=re.DOTALL)
                        clean_text = " ".join([t.strip() for t in text_pieces if t.strip()])
                        matched_kws = [kw for kw in cls.KEYWORD_PATTERNS if re.search(kw, clean_text, re.IGNORECASE)]
                        slides.append({
                            "slide_index": idx + 1,
                            "text": clean_text,
                            "keywords": matched_kws,
                            "is_critical": len(matched_kws) >= 2
                        })
                    return {
                        "file_path": file_path,
                        "format": "ppt_carved_zip",
                        "total_slides": len(slides),
                        "slides": slides
                    }
        except Exception as e:
            return {"file_path": file_path, "format": "ppt", "error": str(e), "slides": []}

        return {"file_path": file_path, "format": "ppt", "error": "Unable to parse legacy PPT", "slides": []}
