from database.connection import get_connection
def remove_missing_metadata_rows(dry_run=True):
    with get_connection() as conn:
        rows=conn.execute("SELECT asset_id,path FROM assets").fetchall()
        missing=[dict(r) for r in rows if not __import__("pathlib").Path(r["path"]).exists()]
        if not dry_run:
            conn.executemany("DELETE FROM assets WHERE asset_id=?",[(r["asset_id"],) for r in missing])
    return {"dry_run":dry_run,"missing":len(missing),"rows":missing}
