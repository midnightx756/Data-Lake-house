from database.connection import get_connection
from security.validation import validate_sql_readonly
def run_readonly_query(sql):
    validate_sql_readonly(sql)
    with get_connection() as conn:
        cur=conn.execute(sql)
        return [dict(r) for r in cur.fetchmany(500)]
