import logging
from pathlib import Path
from config import DATA_DIR
from utils.paths import iter_files
from core.metadata import build_metadata
from core.cpp_blob_bridge import pack_to_blob
from database.repository import AssetRepository
from database.connection import get_connection
from database.audit import log_event

logger = logging.getLogger(__name__)


def scan_folder(folder, max_files=None, progress=None, cancel_event=None):
    repo = AssetRepository()
    scanned = inserted = updated = duplicates = errors = 0
    packed_files = []

    with get_connection() as conn:
        known_hashes = {r[0] for r in conn.execute("SELECT DISTINCT sha256 FROM assets WHERE sha256 IS NOT NULL")}

    for path in iter_files(folder):
        if cancel_event and cancel_event.is_set():
            break
        if max_files is not None and scanned >= max_files:
            break
        scanned += 1
        try:
            item = build_metadata(path, known_hashes)
            outcome = repo.insert_or_update(item)
            if outcome == "inserted":
                inserted += 1
            else:
                updated += 1
            duplicates += item["is_duplicate"]
            known_hashes.add(item["sha256"])
            packed_files.append(item["path"])
        except (OSError, PermissionError, ValueError) as exc:
            errors += 1
            logger.warning("Skipped %s: %s", path, exc)
        if progress and scanned % 25 == 0:
            progress(scanned, inserted, duplicates, errors)

    blob_rows = 0
    blob_path_str = ""
    if packed_files and not (cancel_event and cancel_event.is_set()):
        folder_name = Path(folder).name or "dataset"
        blob_dir = DATA_DIR / "blobs"
        blob_path = blob_dir / f"{folder_name}.blob"
        manifest_path = blob_dir / f"{folder_name}.manifest.csv"
        try:
            pack_res = pack_to_blob(packed_files, blob_path, manifest_path)
            blob_rows = pack_res["manifest_rows"]
            blob_path_str = pack_res["blob_path"]
        except Exception as exc:
            logger.warning("Auto C++ blob pack skipped/failed: %s", exc)

    log_event(
        "scan_completed",
        f"folder={folder}; scanned={scanned}; inserted={inserted}; blob_rows={blob_rows}; errors={errors}",
    )
    return {
        "scanned": scanned,
        "inserted": inserted,
        "updated": updated,
        "duplicates": duplicates,
        "errors": errors,
        "blob_packed": blob_rows,
        "blob_path": blob_path_str,
    }
