from pathlib import Path
def preview_text(path, max_chars=4000):
    p=Path(path)
    if p.suffix.lower() not in {".txt",".md",".csv",".json",".xml",".py",".sql",".log"}: return "Preview unavailable for this file type."
    try: return p.read_text(encoding="utf-8",errors="replace")[:max_chars]
    except OSError as e: return f"Could not preview file: {e}"
