from database.connection import get_connection
def log_event(event_type, detail=""):
    with get_connection() as conn:
        conn.execute("INSERT INTO audit_log(event_type,detail) VALUES(?,?)",(event_type,str(detail)[:2000]))
def recent_events(limit=100):
    with get_connection() as conn:
        return [dict(r) for r in conn.execute("SELECT * FROM audit_log ORDER BY event_id DESC LIMIT ?",(limit,))]
