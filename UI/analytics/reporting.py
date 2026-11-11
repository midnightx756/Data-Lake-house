from database.repository import AssetRepository
def dashboard_metrics(): return AssetRepository().stats()
def extension_breakdown():
    from database.connection import get_connection
    with get_connection() as conn:
        return [dict(r) for r in conn.execute("SELECT COALESCE(extension,'(none)') extension,COUNT(*) count,SUM(size_bytes) bytes FROM assets GROUP BY extension ORDER BY count DESC")]
