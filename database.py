# from pathlib import Path

# from sqlalchemy import create_engine, text
# from sqlalchemy.orm import sessionmaker


# # =====================================================
# # PROJECT PATH
# # =====================================================

# PROJECT_ROOT = (
#     Path(__file__)
#     .resolve()
#     .parent
#     .parent
# )


# # =====================================================
# # DATABASE FOLDER
# # =====================================================

# DATABASE_FOLDER = (
#     PROJECT_ROOT / "database"
# )

# DATABASE_FOLDER.mkdir(
#     exist_ok=True
# )


# # =====================================================
# # DATABASE FILE
# # =====================================================

# DATABASE_FILE = (
#     DATABASE_FOLDER / "lakehouse.db"
# )


# # =====================================================
# # SQLITE DATABASE URL
# # =====================================================

# DATABASE_URL = (
#     f"sqlite:///{DATABASE_FILE}"
# )


# # =====================================================
# # ENGINE
# # =====================================================

# engine = create_engine(
#     DATABASE_URL,
#     connect_args={
#         "check_same_thread": False
#     }
# )


# # =====================================================
# # SESSION
# # =====================================================

# SessionLocal = sessionmaker(
#     bind=engine,
#     autoflush=False,
#     autocommit=False
# )


# # =====================================================
# # INITIALIZE DATABASE
# # =====================================================

# def init_database():

#     # Import here to avoid circular import
#     from models import Base

#     # Create all tables
#     Base.metadata.create_all(
#         bind=engine
#     )

#     # Enable SQLite WAL
#     with engine.connect() as connection:

#         connection.execute(
#             text(
#                 "PRAGMA journal_mode=WAL"
#             )
#         )

#         connection.commit()

#     print(
#         "Database initialized successfully!"
#     )

#     print(
#         f"Database location: {DATABASE_FILE}"
#     )


# # =====================================================
# # GET SESSION
# # =====================================================

# def get_session():

#     return SessionLocal()


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pathlib import Path

# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Database folder
DATABASE_DIR = BASE_DIR / "database"
DATABASE_DIR.mkdir(parents=True, exist_ok=True)

# SQLite database file
DATABASE_PATH = DATABASE_DIR / "lakehouse.db"

# SQLite connection URL
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# ------------------------------------------------------------
# SQLAlchemy Engine
# ------------------------------------------------------------

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={
        "check_same_thread": False
    }
)

# ------------------------------------------------------------
# Session Factory
# ------------------------------------------------------------

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

# ------------------------------------------------------------
# Base Class for SQLAlchemy Models
# ------------------------------------------------------------

Base = declarative_base()


# ------------------------------------------------------------
# Database Session Function
# ------------------------------------------------------------

def get_session():
    """
    Creates and returns a new database session.

    Used by scanner, metadata queries and other
    backend modules.
    """
    return SessionLocal()


# ------------------------------------------------------------
# Initialize Database
# ------------------------------------------------------------

def init_database():
    """
    Creates all tables defined using SQLAlchemy models.
    """

    # Import models here to avoid circular imports
    from .models import FileMetadata

    Base.metadata.create_all(bind=engine)

    print("==========================================")
    print(" Semantic Data Lakehouse Database")
    print("==========================================")
    print(f"Database : {DATABASE_PATH}")
    print("Status   : Ready")
    print("==========================================")


# ------------------------------------------------------------
# Test Database Connection
# ------------------------------------------------------------

def test_connection():
    """
    Tests whether SQLite database connection is working.
    """

    try:
        with engine.connect() as connection:
            print("Database connection successful.")
            return True

    except Exception as error:
        print("Database connection failed.")
        print("Error:", error)
        return False

def migrate_database():
    """Add missing columns to the existing files table."""

    from sqlalchemy import inspect, text
    from .models import FileMetadata

    inspector = inspect(engine)

    if "files" not in inspector.get_table_names():
        Base.metadata.create_all(bind=engine)
        print("Files table created.")
        return

    existing_columns = {
        column["name"]
        for column in inspector.get_columns("files")
    }

    with engine.begin() as connection:
        for column in FileMetadata.__table__.columns:
            if column.name not in existing_columns:
                # SQLite column types from the SQLAlchemy model
                column_type = column.type.compile(
                    dialect=engine.dialect
                )

                # SQLite ALTER TABLE supports adding nullable columns
                # or columns with a suitable constant default.
                statement = (
                    f'ALTER TABLE files ADD COLUMN "{column.name}" '
                    f'{column_type}'
                )

                connection.execute(text(statement))
                print(f"Added column: {column.name}")

    print("Database migration completed.")
# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

if __name__ == "__main__":

    print("\nTesting SDLH Database...\n")

    if test_connection():
        init_database()