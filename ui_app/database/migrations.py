from database.connection import get_connection
def apply_migrations():
    # Schema creation is idempotent; future schema changes should be versioned here.
    from database.schema import create_schema
    with get_connection() as conn: create_schema(conn)
