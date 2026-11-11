from database.connection import get_connection
def quality_summary():
    with get_connection() as conn:
        return {"empty_names":conn.execute("SELECT COUNT(*) FROM assets WHERE name=''").fetchone()[0],
                "missing_hashes":conn.execute("SELECT COUNT(*) FROM assets WHERE sha256 IS NULL OR sha256=''").fetchone()[0],
                "empty_text":conn.execute("SELECT COUNT(*) FROM assets WHERE extracted_text=''").fetchone()[0]}
