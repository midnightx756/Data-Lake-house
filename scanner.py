# import os
# import hashlib
# from pathlib import Path

# from PIL import Image
# from sqlalchemy.exc import IntegrityError

# from database import get_session
# from models import FileMetadata


# # =====================================================
# # SHA-256 HASH
# # =====================================================

# def calculate_hash(filepath):

#     sha256 = hashlib.sha256()

#     with open(filepath, "rb") as file:

#         while True:

#             chunk = file.read(1024 * 1024)

#             if not chunk:
#                 break

#             sha256.update(chunk)

#     return sha256.hexdigest()


# # =====================================================
# # SCAN ONE FILE
# # =====================================================

# def scan_file(filepath):

#     filepath = Path(filepath)

#     filename = filepath.name

#     original_path = str(filepath.resolve())

#     size = filepath.stat().st_size

#     extension = filepath.suffix.lower()

#     file_hash = calculate_hash(filepath)

#     width = None
#     height = None

#     # Image dimensions
#     try:

#         with Image.open(filepath) as image:

#             width, height = image.size

#     except Exception:
#         pass

#     # Parent folder becomes label
#     # cat/cat1.jpg -> cat
#     # dog/dog1.jpg -> dog

#     label = filepath.parent.name

#     return {
#         "filename": filename,
#         "original_path": original_path,
#         "size": size,
#         "extension": extension,
#         "file_hash": file_hash,
#         "label": label,
#         "width": width,
#         "height": height
#     }


# # =====================================================
# # SCAN DIRECTORY
# # =====================================================

# def scan_directory(directory):

#     directory = Path(directory)

#     if not directory.exists():

#         print(
#             f"ERROR: Folder does not exist: {directory}"
#         )

#         return

#     session = get_session()

#     indexed_count = 0
#     duplicate_count = 0
#     error_count = 0

#     # Hashes already seen during THIS scan
#     scanned_hashes = set()

#     print()
#     print(
#         f"Scanning folder: {directory.resolve()}"
#     )
#     print("-" * 60)

#     try:

#         for root, dirs, files in os.walk(directory):

#             for filename in files:

#                 filepath = Path(root) / filename

#                 try:

#                     # ---------------------------------
#                     # GET METADATA
#                     # ---------------------------------

#                     metadata = scan_file(filepath)

#                     file_hash = metadata["file_hash"]

#                     # ---------------------------------
#                     # DUPLICATE IN CURRENT SCAN
#                     # ---------------------------------

#                     if file_hash in scanned_hashes:

#                         print(
#                             f"DUPLICATE: {filename}"
#                         )

#                         duplicate_count += 1

#                         continue

#                     # ---------------------------------
#                     # CHECK DATABASE
#                     # ---------------------------------

#                     existing = (
#                         session
#                         .query(FileMetadata)
#                         .filter(
#                             FileMetadata.file_hash == file_hash
#                         )
#                         .first()
#                     )

#                     if existing:

#                         print(
#                             f"DUPLICATE: {filename}"
#                         )

#                         duplicate_count += 1

#                         # Remember hash
#                         scanned_hashes.add(file_hash)

#                         continue

#                     # ---------------------------------
#                     # ADD HASH TO CURRENT SCAN
#                     # ---------------------------------

#                     scanned_hashes.add(file_hash)

#                     # ---------------------------------
#                     # CREATE DATABASE RECORD
#                     # ---------------------------------

#                     record = FileMetadata(
#                         **metadata
#                     )

#                     session.add(record)

#                     # IMPORTANT:
#                     # Immediately flush this record
#                     # so next duplicate check can see it.

#                     session.flush()

#                     indexed_count += 1

#                     print(
#                         f"INDEXED: {filename}"
#                     )

#                 except IntegrityError:

#                     # In case a race/duplicate slips through
#                     session.rollback()

#                     duplicate_count += 1

#                     print(
#                         f"DUPLICATE: {filename}"
#                     )

#                 except Exception as error:

#                     error_count += 1

#                     print(
#                         f"ERROR: {filepath}"
#                     )

#                     print(
#                         f"       {error}"
#                     )

#                     session.rollback()

#         # ---------------------------------------------
#         # FINAL COMMIT
#         # ---------------------------------------------

#         session.commit()

#     except Exception as error:

#         session.rollback()

#         print()
#         print(
#             "DATABASE ERROR:"
#         )
#         print(error)

#     finally:

#         session.close()

#     # =================================================
#     # FINAL RESULT
#     # =================================================

#     print()
#     print("=" * 60)
#     print("SCAN COMPLETE")
#     print("=" * 60)

#     print(
#         f"New files indexed : {indexed_count}"
#     )

#     print(
#         f"Duplicates found  : {duplicate_count}"
#     )

#     print(
#         f"Errors            : {error_count}"
#     )


# # =====================================================
# # MAIN
# # =====================================================

# if __name__ == "__main__":

#     PROJECT_ROOT = (
#         Path(__file__)
#         .resolve()
#         .parent
#         .parent
#     )

#     TEST_DATASET = (
#         PROJECT_ROOT
#         / "data"
#         / "test_dataset"
#     )

#     scan_directory(
#         TEST_DATASET
#     )



import argparse
import hashlib
from pathlib import Path

from sqlalchemy.exc import IntegrityError

from .database import get_session
from .models import FileMetadata


BATCH_SIZE = 500

DEFAULT_DATASET = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "test_dataset"
)


def calculate_hash(file_path):
    """Calculate SHA-256 without loading the entire file into memory."""

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


def get_image_dimensions(file_path):
    """Return image width and height, or None for non-images."""

    try:
        from PIL import Image

        with Image.open(file_path) as image:
            return image.width, image.height

    except Exception:
        return None, None


def scan_dataset(dataset_path=DEFAULT_DATASET):
    dataset_path = Path(dataset_path).resolve()

    if not dataset_path.is_dir():
        print(f"Dataset folder not found: {dataset_path}")
        return

    session = get_session()

    scanned = 0
    inserted = 0
    duplicates = 0
    errors = 0
    pending_hashes = set()

    try:
        for file_path in dataset_path.rglob("*"):

            if not file_path.is_file():
                continue

            scanned += 1

            try:
                file_hash = calculate_hash(file_path)

                # Detect duplicate content within this batch
                if file_hash in pending_hashes:
                    duplicates += 1
                    continue

                # Check hashes already stored in the database
                exists = (
                    session.query(FileMetadata.id)
                    .filter(FileMetadata.file_hash == file_hash)
                    .first()
                )

                if exists:
                    duplicates += 1
                    continue

                width, height = get_image_dimensions(file_path)

                size = file_path.stat().st_size
                extension = file_path.suffix.lower()
                label = file_path.parent.name

                # Only use columns available in the current model
                available_columns = {
                    column.name
                    for column in FileMetadata.__table__.columns
                }

                metadata = {
                    "asset_id": file_hash,
                    "filename": file_path.name,
                    "original_path": str(file_path),
                    "extension": extension,
                    "label": label,
                    "file_hash": file_hash,
                    "size": size,
                    "width": width,
                    "height": height,
                    "version": 1,
                }

                metadata = {
                    key: value
                    for key, value in metadata.items()
                    if key in available_columns
                }

                # Save each file inside a nested transaction
                # so one failed insert doesn't discard the batch.
                try:
                    with session.begin_nested():
                        session.add(FileMetadata(**metadata))
                        session.flush()

                    pending_hashes.add(file_hash)
                    inserted += 1

                except IntegrityError:
                    duplicates += 1

                # Commit in batches to avoid one huge transaction
                if inserted > 0 and inserted % BATCH_SIZE == 0:
                    session.commit()
                    pending_hashes.clear()

                    print(
                        f"Scanned: {scanned} | "
                        f"Inserted: {inserted} | "
                        f"Duplicates: {duplicates}"
                    )

            except Exception as error:
                errors += 1
                print(f"Could not process {file_path}: {error}")

        session.commit()

        print("\n===== SCAN SUMMARY =====")
        print(f"Files encountered : {scanned}")
        print(f"Metadata inserted : {inserted}")
        print(f"Duplicates skipped: {duplicates}")
        print(f"Errors            : {errors}")

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="SDLH metadata dataset scanner"
    )

    parser.add_argument(
        "dataset",
        nargs="?",
        default=str(DEFAULT_DATASET),
        help="Path to the dataset folder",
    )

    args = parser.parse_args()
    scan_dataset(args.dataset)