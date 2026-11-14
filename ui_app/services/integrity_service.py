from core.integrity import verify_assets
from core.blob_integrity import verify_blob_assets


def run_integrity_check(limit=1000):
    return verify_assets(limit)


def run_blob_integrity_check():
    return verify_blob_assets()
