import csv
from database.repository import AssetRepository
def export_assets(destination):
    rows=AssetRepository().search(limit=5000)
    if not rows: return 0
    with open(destination,"w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0].keys())); writer.writeheader(); writer.writerows(rows)
    return len(rows)
