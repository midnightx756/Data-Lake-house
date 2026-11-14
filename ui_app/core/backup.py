import shutil
from datetime import datetime
from config import DB_PATH, DATA_DIR
def backup_database(destination=None):
    target=destination or (DATA_DIR/"backups"/f"sdlh_{datetime.now():%Y%m%d_%H%M%S}.db")
    target=__import__("pathlib").Path(target); target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(DB_PATH,target); return str(target)
