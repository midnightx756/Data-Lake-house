"""Simple integrity check for assets stored inside SDLH blob files."""
import hashlib
import os
import sys

from database.connection import get_connection

HEADER_SIZE = 64


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def verify_blob_assets():
    """Check each blob record's header, payload size and payload hash."""
    with get_connection() as conn:
        table = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='blob_assets'"
        ).fetchone()
        if not table:
            return {
                "checked": 0, "valid": 0, "corrupted": 0, "errors": 0,
                "problems": [("blob_assets", "No blob records found yet")]
            }

        rows = conn.execute("""
            SELECT source_path, blob_path, byte_offset, payload_size
            FROM blob_assets
            ORDER BY blob_asset_id
        """).fetchall()

        stored_hashes = {
            row["path"]: row["sha256"]
            for row in conn.execute(
                "SELECT path, sha256 FROM assets WHERE sha256 IS NOT NULL"
            ).fetchall()
        }

    checked = 0
    valid = 0
    corrupted = 0
    errors = 0
    problems = []

    for row in rows:
        checked += 1
        source = row["source_path"]
        blob_path = row["blob_path"]
        offset = int(row["byte_offset"])
        expected_size = int(row["payload_size"])

        try:
            if not os.path.isfile(blob_path):
                errors += 1
                problems.append((blob_path, "Blob file missing"))
                continue

            with open(blob_path, "rb") as blob:
                blob.seek(0, os.SEEK_END)
                blob_size = blob.tell()

                if offset < 0 or offset + HEADER_SIZE > blob_size:
                    corrupted += 1
                    problems.append((source, "Invalid blob offset"))
                    continue

                blob.seek(offset)
                header = blob.read(HEADER_SIZE)

                if len(header) != HEADER_SIZE or header[:4] != b"SDLH":
                    corrupted += 1
                    problems.append((source, "Invalid SDLH header"))
                    continue

                actual_size = int.from_bytes(
                    header[12:20], byteorder=sys.byteorder
                )

                if actual_size != expected_size:
                    corrupted += 1
                    problems.append((source, "Payload size mismatch"))
                    continue

                if offset + HEADER_SIZE + actual_size > blob_size:
                    corrupted += 1
                    problems.append((source, "Payload extends beyond blob"))
                    continue

                payload = blob.read(actual_size)

            expected_hash = stored_hashes.get(source)
            if expected_hash and sha256_bytes(payload) != expected_hash:
                corrupted += 1
                problems.append((source, "Payload hash mismatch"))
                continue

            valid += 1

        except OSError as error:
            errors += 1
            problems.append((source, str(error)))

    return {
        "checked": checked,
        "valid": valid,
        "corrupted": corrupted,
        "errors": errors,
        "problems": problems
    }
