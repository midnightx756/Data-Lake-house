from database.connection import get_connection
def list_jobs(limit=100):
    with get_connection() as conn: return [dict(r) for r in conn.execute("SELECT * FROM jobs ORDER BY job_id DESC LIMIT ?",(limit,))]
