"""Wrapper that builds and calls the C++ core_cpp binary (bin/sdlh) via Makefile."""
import csv
import shutil
import subprocess
import tempfile
from pathlib import Path
from database.connection import get_connection
from config import BASE_DIR

REPO_ROOT = BASE_DIR.parent
BINARY = REPO_ROOT / "bin" / "sdlh"


def compile_engine():
    if BINARY.is_file():
        return str(BINARY)
    if not shutil.which("g++") or not shutil.which("make"):
        raise RuntimeError("Install g++ and make inside WSL / Fedora.")
    result = subprocess.run(
        ["make"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.returncode:
        raise RuntimeError("C++ build failed:\n" + (result.stderr or result.stdout)[-4000:])
    return str(BINARY)


def pack_to_blob(file_paths, blob_path, manifest_path):
    files = [str(Path(p).resolve()) for p in file_paths if Path(p).is_file()]
    if not files:
        raise ValueError("Select at least one existing file to pack.")
    binary = compile_engine()
    blob = Path(blob_path).resolve()
    manifest = Path(manifest_path).resolve()
    blob.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)

    result = subprocess.run(
        [binary, "pack", str(blob), str(manifest), *files],
        capture_output=True,
        text=True,
        timeout=600,
    )
    if result.returncode:
        raise RuntimeError("C++ pack failed:\n" + (result.stderr or result.stdout)[-4000:])

    imported = 0
    with get_connection() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS blob_assets(
            blob_asset_id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_path TEXT NOT NULL, blob_path TEXT NOT NULL, manifest_path TEXT NOT NULL,
            byte_offset INTEGER NOT NULL, payload_size INTEGER NOT NULL,
            is_duplicate INTEGER NOT NULL DEFAULT 0, packed_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(source_path, blob_path))""")
        with manifest.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                source = str(Path(row["original_name"]).resolve())
                conn.execute(
                    """INSERT INTO blob_assets(source_path,blob_path,manifest_path,byte_offset,payload_size,is_duplicate)
                    VALUES(?,?,?,?,?,?)
                    ON CONFLICT(source_path,blob_path) DO UPDATE SET manifest_path=excluded.manifest_path,
                    byte_offset=excluded.byte_offset,payload_size=excluded.payload_size,is_duplicate=excluded.is_duplicate,
                    packed_at=CURRENT_TIMESTAMP""",
                    (
                        source,
                        str(blob),
                        str(manifest),
                        int(row["byte_offset"]),
                        int(row["payload_size"]),
                        int(row["is_duplicate"]),
                    ),
                )
                imported += 1
        conn.execute(
            "INSERT INTO audit_log(event_type,detail) VALUES(?,?)",
            ("cpp_blob_pack", f"blob={blob}; manifest={manifest}; imported={imported}"),
        )
    return {
        "blob_path": str(blob),
        "manifest_path": str(manifest),
        "manifest_rows": imported,
        "stdout": result.stdout,
    }


def extract_asset_bytes(blob_path, offset):
    """Run C++ mmap extraction silently and return (raw_bytes, log_text)."""
    binary = compile_engine()
    resolved_blob = str(Path(blob_path).resolve())
    if not Path(resolved_blob).is_file():
        raise FileNotFoundError(f"Blob file not found: {resolved_blob}")

    with tempfile.NamedTemporaryFile(delete=False) as tf:
        tmp_path = Path(tf.name)
    tmp_path.unlink(missing_ok=True)

    result = subprocess.run(
        [binary, "extract", resolved_blob, str(int(offset)), str(tmp_path)],
        capture_output=True,
        timeout=120,
    )
    stdout_bytes = result.stdout or b""
    stderr_text = (result.stderr or b"").decode("utf-8", errors="replace").strip()

    if result.returncode != 0:
        tmp_path.unlink(missing_ok=True)
        raise RuntimeError(stderr_text or stdout_bytes.decode("utf-8", errors="replace"))

    if tmp_path.is_file():
        data = tmp_path.read_bytes()
        tmp_path.unlink(missing_ok=True)
        return data, stdout_bytes.decode("utf-8", errors="replace")

    # Fallback for unedited 2-arg mmap_extractor.cpp (writes "File Data: <bytes>\n" to stdout)
    marker = b"File Data: "
    idx = stdout_bytes.find(marker)
    if idx != -1:
        payload = stdout_bytes[idx + len(marker):]
        if payload.endswith(b"\n"):
            payload = payload[:-1]
        log_text = stdout_bytes[:idx].decode("utf-8", errors="replace").strip()
        return payload, log_text

    raise RuntimeError(stderr_text or "C++ mmap extractor failed to return payload.")


def extract_from_blob(blob_path, offset, output_path):
    data, log_text = extract_asset_bytes(blob_path, offset)
    Path(output_path).write_bytes(data)
    return log_text
