from database.connection import get_connection
class AssetRepository:
    def insert_or_update(self, item):
        with get_connection() as conn:
            old = conn.execute("SELECT asset_id FROM assets WHERE path=?", (item["path"],)).fetchone()
            if old:
                conn.execute("""UPDATE assets SET name=?,extension=?,mime_type=?,size_bytes=?,
                  modified_at=?,sha256=?,is_duplicate=?,extracted_text=?,status='indexed' WHERE path=?""",
                  (item["name"],item["extension"],item["mime_type"],item["size_bytes"],
                   item["modified_at"],item["sha256"],item["is_duplicate"],item["extracted_text"],item["path"]))
                return "updated"
            conn.execute("""INSERT INTO assets(path,name,extension,mime_type,size_bytes,modified_at,
              sha256,is_duplicate,extracted_text) VALUES(?,?,?,?,?,?,?,?,?)""",
              tuple(item[k] for k in ("path","name","extension","mime_type","size_bytes","modified_at",
                                      "sha256","is_duplicate","extracted_text")))
            return "inserted"
    def search(self, query="", extension="", limit=500):
        sql = "SELECT * FROM assets WHERE 1=1"
        args=[]
        if query:
            sql += " AND (name LIKE ? OR path LIKE ? OR extracted_text LIKE ?)"
            args += [f"%{query}%"]*3
        if extension:
            sql += " AND extension=?"; args.append(extension.lower())
        sql += " ORDER BY name LIMIT ?"; args.append(max(1,min(int(limit),5000)))
        with get_connection() as conn: return [dict(r) for r in conn.execute(sql,args)]
    def stats(self):
        with get_connection() as conn:
            row=conn.execute("SELECT COUNT(*) n,COALESCE(SUM(size_bytes),0) bytes,COUNT(DISTINCT extension) types FROM assets").fetchone()
            dup=conn.execute("SELECT COUNT(*) FROM assets WHERE is_duplicate=1").fetchone()[0]
            jobs=conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
        return {"assets":row["n"],"bytes":row["bytes"],"types":row["types"],"duplicates":dup,"jobs":jobs}
