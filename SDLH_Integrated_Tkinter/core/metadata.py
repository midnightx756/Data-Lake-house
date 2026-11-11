import os
from pathlib import Path
from utils.file_types import describe_file
from utils.hashing import sha256_file
from core.text_extractor import extract_text
def build_metadata(path, known_hashes):
    p=Path(path); st=p.stat(); digest=sha256_file(p)
    return {"path":str(p.resolve()),"name":p.name,"extension":p.suffix.lower(),
      "mime_type":describe_file(p),"size_bytes":st.st_size,"modified_at":st.st_mtime,
      "sha256":digest,"is_duplicate":int(digest in known_hashes),
      "extracted_text":extract_text(p)}
