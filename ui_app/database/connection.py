import sqlite3
from config import DB_PATH
def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA journal_mode=WAL")
    return conn
def initialize_database():
    from database.schema import create_schema
    with get_connection() as conn: create_schema(conn)
