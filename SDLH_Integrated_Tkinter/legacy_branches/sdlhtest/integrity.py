
import hashlib
from pathlib import Path

from .database import get_session
from .models import FileMetadata


def calculate_hash(file_path):
    """Calculate SHA-256 in chunks to reduce memory usage."""

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


def verify_integrity():
    """Compare stored metadata against actual files."""

    session = get_session()

    verified = 0
    hash_mismatch = 0
    size_mismatch = 0
    missing = 0
    errors = 0

    try:
        records = session.query(FileMetadata).yield_per(500)

        for record in records:
            path = Path(record.original_path)

            if not path.is_file():
                missing += 1
                print(f"MISSING: {record.filename}")
                continue

            try:
                actual_size = path.stat().st_size

                if actual_size != record.size:
                    size_mismatch += 1
                    print(
                        f"SIZE MISMATCH: {record.filename} | "
                        f"DB={record.size} | Actual={actual_size}"
                    )
                    continue

                actual_hash = calculate_hash(path)

                if actual_hash != record.file_hash:
                    hash_mismatch += 1
                    print(f"HASH MISMATCH: {record.filename}")
                else:
                    verified += 1
                    print(f"VERIFIED: {record.filename}")

            except OSError as error:
                errors += 1
                print(f"ERROR: {record.filename} | {error}")

        print("\n===== INTEGRITY REPORT =====")
        print(f"Verified       : {verified}")
        print(f"Hash mismatches: {hash_mismatch}")
        print(f"Size mismatches: {size_mismatch}")
        print(f"Missing files  : {missing}")
        print(f"Errors         : {errors}")
        print("============================")

    finally:
        session.close()


if __name__ == "__main__":
    verify_integrity()
