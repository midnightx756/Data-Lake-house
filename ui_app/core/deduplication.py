from database.connection import get_connection
def duplicate_groups():
    with get_connection() as conn:
        return [dict(r) for r in conn.execute("""SELECT sha256,COUNT(*) count,GROUP_CONCAT(name, ' | ') names
          FROM assets WHERE sha256 IS NOT NULL GROUP BY sha256 HAVING COUNT(*)>1 ORDER BY count DESC""")]
