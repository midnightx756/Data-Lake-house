import hashlib
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from core.blob_integrity import verify_blob_assets


class BlobIntegrityTests(unittest.TestCase):
    def test_valid_blob_record(self):
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            source = folder / "sample.txt"
            blob = folder / "data.blob"
            source.write_bytes(b"hello SDLH")
            payload = source.read_bytes()

            header = bytearray(64)
            header[:4] = b"SDLH"
            header[12:20] = len(payload).to_bytes(8, byteorder="little")
            blob.write_bytes(header + payload)

            db = folder / "test.db"
            conn = sqlite3.connect(db)
            conn.row_factory = sqlite3.Row
            conn.execute("""
                CREATE TABLE blob_assets (
                    blob_asset_id INTEGER PRIMARY KEY,
                    source_path TEXT, blob_path TEXT,
                    byte_offset INTEGER, payload_size INTEGER
                )
            """)
            conn.execute("""
                CREATE TABLE assets (path TEXT, sha256 TEXT)
            """)
            conn.execute(
                "INSERT INTO blob_assets VALUES (1, ?, ?, 0, ?)",
                (str(source), str(blob), len(payload))
            )
            conn.execute(
                "INSERT INTO assets VALUES (?, ?)",
                (str(source), hashlib.sha256(payload).hexdigest())
            )
            conn.commit()
            conn.close()

            with patch("database.connection.DB_PATH", db):
                result = verify_blob_assets()

            self.assertEqual(result["checked"], 1)
            self.assertEqual(result["valid"], 1)
            self.assertEqual(result["corrupted"], 0)


if __name__ == "__main__":
    unittest.main()
