from pathlib import Path
APP_NAME = "Semantic Data Lakehouse"
VERSION = "1.0.0"
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "sdlh_metadata.db"
LOG_DIR = BASE_DIR / "logs"
DEFAULT_BATCH_SIZE = 250
HASH_CHUNK_SIZE = 1024 * 1024
SUPPORTED_TEXT_EXTENSIONS = {".txt", ".md", ".csv", ".json", ".xml", ".py", ".sql", ".log"}
