from pathlib import Path
from config import SUPPORTED_TEXT_EXTENSIONS
def extract_text(path, max_bytes=1_000_000):
    p=Path(path)
    if p.suffix.lower() in SUPPORTED_TEXT_EXTENSIONS:
        try:
            with p.open("rb") as f: return f.read(max_bytes).decode("utf-8",errors="replace")
        except OSError: return ""
    if p.suffix.lower()==".pdf":
        try:
            from pypdf import PdfReader
            reader=PdfReader(str(p))
            return "\\n".join((page.extract_text() or "") for page in reader.pages[:20])[:max_bytes]
        except Exception: return ""
    return ""
