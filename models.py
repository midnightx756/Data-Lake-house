# from datetime import datetime, timezone

# from sqlalchemy import (
#     Column,
#     Integer,
#     String,
#     BigInteger,
#     DateTime
# )

# from sqlalchemy.orm import declarative_base


# # =====================================================
# # BASE
# # =====================================================

# Base = declarative_base()


# # =====================================================
# # FILE METADATA TABLE
# # =====================================================

# class FileMetadata(Base):

#     __tablename__ = "files"

#     # -------------------------------------------------
#     # PRIMARY KEY
#     # -------------------------------------------------

#     id = Column(
#         Integer,
#         primary_key=True,
#         autoincrement=True
#     )

#     # -------------------------------------------------
#     # BASIC FILE INFORMATION
#     # -------------------------------------------------

#     filename = Column(
#         String,
#         nullable=False
#     )

#     original_path = Column(
#         String,
#         nullable=False
#     )

#     extension = Column(
#         String
#     )

#     size = Column(
#         BigInteger
#     )

#     # -------------------------------------------------
#     # FILE INTEGRITY
#     # -------------------------------------------------

#     file_hash = Column(
#         String,
#         unique=True,
#         index=True
#     )

#     # -------------------------------------------------
#     # AI / SEMANTIC LABEL
#     # -------------------------------------------------

#     label = Column(
#         String,
#         index=True,
#         nullable=True
#     )

#     # -------------------------------------------------
#     # IMAGE INFORMATION
#     # -------------------------------------------------

#     width = Column(
#         Integer,
#         nullable=True
#     )

#     height = Column(
#         Integer,
#         nullable=True
#     )

#     # -------------------------------------------------
#     # C++ BLOB ENGINE INFORMATION
#     # -------------------------------------------------

#     blob_id = Column(
#         Integer,
#         nullable=True
#     )

#     offset = Column(
#         BigInteger,
#         nullable=True
#     )

#     length = Column(
#         BigInteger,
#         nullable=True
#     )

#     # -------------------------------------------------
#     # DATASET VERSION
#     # -------------------------------------------------

#     version = Column(
#         Integer,
#         default=1
#     )

#     # -------------------------------------------------
#     # CREATED TIME
#     # -------------------------------------------------

#     created_at = Column(
#         DateTime,
#         default=lambda: datetime.now(timezone.utc)
#     )

#     # -------------------------------------------------
#     # DISPLAY OBJECT
#     # -------------------------------------------------

#     def __repr__(self):

#         return (
#             f"<FileMetadata("
#             f"id={self.id}, "
#             f"filename='{self.filename}', "
#             f"label='{self.label}'"
#             f")>"
#         )



from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    BigInteger,
    DateTime,
    Index,
)
from .database import Base


class FileMetadata(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)

    # File identification
    asset_id = Column(String(64), unique=True, index=True)
    filename = Column(String(255), nullable=False, index=True)
    original_path = Column(String(2048), nullable=False)
    extension = Column(String(20), index=True)
    label = Column(String(255), index=True)

    # Integrity and deduplication
    file_hash = Column(String(64), unique=True, index=True)
    size = Column(BigInteger, default=0, nullable=False)

    # Image metadata
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)

    # Blob storage integration fields
    blob_id = Column(String(255), nullable=True, index=True)
    blob_path = Column(String(2048), nullable=True)
    offset = Column(BigInteger, nullable=True)
    byte_offset = Column(BigInteger, nullable=True)
    length = Column(BigInteger, nullable=True)
    payload_size = Column(BigInteger, nullable=True)

    # Dataset version
    version = Column(Integer, default=1, nullable=False)

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )


# Frequently used metadata filters
Index("idx_files_label_extension", FileMetadata.label,
      FileMetadata.extension)

Index("idx_files_size", FileMetadata.size)