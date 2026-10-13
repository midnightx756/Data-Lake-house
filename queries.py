# from database import get_session
# from models import FileMetadata


# # =====================================================
# # SHOW ALL FILES
# # =====================================================

# def show_all_files():

#     session = get_session()

#     files = (
#         session
#         .query(FileMetadata)
#         .order_by(
#             FileMetadata.id
#         )
#         .all()
#     )

#     print()

#     print(
#         "=" * 100
#     )

#     print(
#         f"{'ID':<5}"
#         f"{'Filename':<20}"
#         f"{'Label':<15}"
#         f"{'Size':<12}"
#         f"{'Width':<8}"
#         f"{'Height':<8}"
#     )

#     print(
#         "=" * 100
#     )

#     for file in files:

#         print(
#             f"{file.id:<5}"
#             f"{file.filename:<20}"
#             f"{str(file.label):<15}"
#             f"{str(file.size):<12}"
#             f"{str(file.width):<8}"
#             f"{str(file.height):<8}"
#         )

#     print(
#         "=" * 100
#     )

#     print(
#         f"Total files: {len(files)}"
#     )

#     session.close()


# # =====================================================
# # SEARCH BY LABEL
# # =====================================================

# def search_by_label(label):

#     session = get_session()

#     files = (
#         session
#         .query(FileMetadata)
#         .filter(
#             FileMetadata.label == label
#         )
#         .all()
#     )

#     print()

#     print(
#         f"Files with label: {label}"
#     )

#     print(
#         "-" * 60
#     )

#     for file in files:

#         print(
#             f"ID: {file.id} | "
#             f"File: {file.filename} | "
#             f"Resolution: "
#             f"{file.width}x{file.height}"
#         )

#     print(
#         f"Total results: {len(files)}"
#     )

#     session.close()


# # =====================================================
# # SEARCH HIGH RESOLUTION
# # =====================================================

# def search_high_resolution():

#     session = get_session()

#     files = (
#         session
#         .query(FileMetadata)
#         .filter(
#             FileMetadata.width > 1080
#         )
#         .all()
#     )

#     print()

#     print(
#         "High-resolution images:"
#     )

#     print(
#         "-" * 60
#     )

#     for file in files:

#         print(
#             f"{file.filename} "
#             f"-> "
#             f"{file.width}x{file.height}"
#         )

#     print(
#         f"Total results: {len(files)}"
#     )

#     session.close()


# # =====================================================
# # SEARCH BY EXTENSION
# # =====================================================

# def search_by_extension(extension):

#     session = get_session()

#     if not extension.startswith("."):

#         extension = "." + extension

#     files = (
#         session
#         .query(FileMetadata)
#         .filter(
#             FileMetadata.extension == extension
#         )
#         .all()
#     )

#     print()

#     print(
#         f"Files with extension: {extension}"
#     )

#     print(
#         "-" * 60
#     )

#     for file in files:

#         print(
#             f"{file.filename} "
#             f"-> "
#             f"{file.size} bytes"
#         )

#     print(
#         f"Total results: {len(files)}"
#     )

#     session.close()


# # =====================================================
# # MAIN
# # =====================================================

# if __name__ == "__main__":

#     print()

#     print(
#         "SEMANTIC DATA LAKEHOUSE"
#     )

#     print(
#         "DATABASE QUERY TEST"
#     )

#     print(
#         "=" * 60
#     )

#     # 1. Show everything
#     show_all_files()

#     # 2. Search cats
#     search_by_label(
#         "cat"
#     )

#     # 3. Search high resolution
#     search_high_resolution()

#     # 4. Search JPG
#     search_by_extension(
#         ".jpg"
#     )



from sqlalchemy import func, or_

from .database import get_session
from .models import FileMetadata


def get_statistics():
    """Return basic dataset statistics using SQL queries."""

    session = get_session()

    try:
        total_files = session.query(
            func.count(FileMetadata.id)
        ).scalar() or 0

        total_size = session.query(
            func.coalesce(func.sum(FileMetadata.size), 0)
        ).scalar() or 0

        categories = session.query(
            func.count(func.distinct(FileMetadata.label))
        ).scalar() or 0

        extensions = (
            session.query(
                FileMetadata.extension,
                func.count(FileMetadata.id).label("file_count"),
            )
            .group_by(FileMetadata.extension)
            .all()
        )

        return {
            "total_files": total_files,
            "total_size_bytes": total_size,
            "categories": categories,
            "extensions": [
                {"extension": ext or "(none)", "count": count}
                for ext, count in extensions
            ],
        }

    finally:
        session.close()


def search_files(term="", label=None, extension=None, limit=50):
    """Search metadata by filename, label, extension or hash."""

    session = get_session()

    try:
        query = session.query(FileMetadata)

        if term:
            pattern = f"%{term}%"

            query = query.filter(
                or_(
                    FileMetadata.filename.ilike(pattern),
                    FileMetadata.label.ilike(pattern),
                    FileMetadata.file_hash.ilike(pattern),
                    FileMetadata.extension.ilike(pattern),
                )
            )

        if label:
            query = query.filter(FileMetadata.label == label)

        if extension:
            query = query.filter(
                FileMetadata.extension == extension.lower()
            )

        records = (
            query.order_by(FileMetadata.id)
            .limit(max(1, min(limit, 500)))
            .all()
        )

        return [
            {
                "id": record.id,
                "filename": record.filename,
                "path": record.original_path,
                "extension": record.extension,
                "label": record.label,
                "size": record.size,
                "hash": record.file_hash,
                "width": record.width,
                "height": record.height,
                "blob_id": record.blob_id,
                "offset": record.offset,
                "length": record.length,
            }
            for record in records
        ]

    finally:
        session.close()


def get_category_counts():
    """Count files in each semantic label/category."""

    session = get_session()

    try:
        results = (
            session.query(
                FileMetadata.label,
                func.count(FileMetadata.id).label("total"),
            )
            .group_by(FileMetadata.label)
            .order_by(func.count(FileMetadata.id).desc())
            .all()
        )

        return [
            {"label": label or "Uncategorized", "total": total}
            for label, total in results
        ]

    finally:
        session.close()


if __name__ == "__main__":
    print("===== DATASET STATISTICS =====")
    print(get_statistics())

    print("\n===== CATEGORY DISTRIBUTION =====")
    for category in get_category_counts():
        print(category)

    print("\n===== FIRST 10 FILES =====")
    for record in search_files(limit=10):
        print(record)