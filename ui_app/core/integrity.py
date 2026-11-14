from pathlib import Path
from utils.hashing import sha256_file
from database.connection import get_connection
def verify_assets(limit=1000):
    checked=missing=changed=0; problems=[]
    with get_connection() as conn:
        rows=conn.execute("SELECT path,size_bytes,sha256 FROM assets ORDER BY asset_id LIMIT ?",(limit,)).fetchall()
    for row in rows:
        checked+=1; p=Path(row["path"])
        if not p.exists(): missing+=1; problems.append((str(p),"missing")); continue
        try:
            if p.stat().st_size != row["size_bytes"] or (row["sha256"] and sha256_file(p)!=row["sha256"]):
                changed+=1; problems.append((str(p),"changed"))
        except OSError: missing+=1; problems.append((str(p),"unreadable"))
    return {"checked":checked,"missing":missing,"changed":changed,"problems":problems}
