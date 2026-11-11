import sqlite3, unittest
from database.schema import create_schema
class SchemaTests(unittest.TestCase):
    def test_schema_created(self):
        conn=sqlite3.connect(":memory:"); create_schema(conn)
        names={r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        self.assertTrue({"assets","jobs","audit_log"}.issubset(names))
if __name__=="__main__": unittest.main()
