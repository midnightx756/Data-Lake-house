import logging
from utils.paths import iter_files
from core.metadata import build_metadata
from database.repository import AssetRepository
from database.connection import get_connection
from database.audit import log_event
logger=logging.getLogger(__name__)
def scan_folder(folder, max_files=None, progress=None, cancel_event=None):
    repo=AssetRepository(); scanned=inserted=updated=duplicates=errors=0
    with get_connection() as conn:
        known_hashes={r[0] for r in conn.execute("SELECT DISTINCT sha256 FROM assets WHERE sha256 IS NOT NULL")}
    for path in iter_files(folder):
        if cancel_event and cancel_event.is_set(): break
        if max_files is not None and scanned>=max_files: break
        scanned+=1
        try:
            item=build_metadata(path,known_hashes)
            outcome=repo.insert_or_update(item)
            if outcome=="inserted": inserted+=1
            else: updated+=1
            duplicates+=item["is_duplicate"]
            known_hashes.add(item["sha256"])
        except (OSError, PermissionError, ValueError) as exc:
            errors+=1; logger.warning("Skipped %s: %s",path,exc)
        if progress and scanned%25==0: progress(scanned,inserted,duplicates,errors)
    log_event("scan_completed",f"folder={folder}; scanned={scanned}; inserted={inserted}; errors={errors}")
    return {"scanned":scanned,"inserted":inserted,"updated":updated,"duplicates":duplicates,"errors":errors}
