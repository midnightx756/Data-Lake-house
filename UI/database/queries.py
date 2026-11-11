from database.connection import get_connection
def table_names():
    with get_connection() as conn:
        return [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
def table_info(name):
    if not name.replace("_","").isalnum(): raise ValueError("Invalid table name")
    with get_connection() as conn:
        return [dict(r) for r in conn.execute(f'PRAGMA table_info("{name}")')]
