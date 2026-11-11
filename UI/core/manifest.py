import csv
from database.connection import get_connection
def export_manifest(path):
    with get_connection() as conn: rows=[dict(r) for r in conn.execute("SELECT * FROM assets ORDER BY asset_id")]
    if not rows: return 0
    with open(path,"w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    return len(rows)
