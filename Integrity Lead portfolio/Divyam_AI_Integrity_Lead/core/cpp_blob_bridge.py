"""Safe wrapper for the portable C++ blob packer. Requires g++/clang++ on PATH."""
import csv
import shutil
import subprocess
from pathlib import Path
from database.connection import get_connection
from config import BASE_DIR

SOURCE = BASE_DIR / "cpp_engine" / "sdlh_blob.cpp"
BUILD_DIR = BASE_DIR / "build"
BINARY = BUILD_DIR / ("sdlh_blob.exe" if __import__("os").name == "nt" else "sdlh_blob")

def compiler_name():
    return shutil.which("g++") or shutil.which("clang++")

def compile_engine():
    compiler = compiler_name()
    if not compiler:
        raise RuntimeError("C++ compiler not found. Install MinGW-w64 (g++) and add its bin folder to PATH, then restart VS Code.")
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    result = subprocess.run([compiler, "-std=c++17", "-O2", str(SOURCE), "-o", str(BINARY)],
                            capture_output=True, text=True, timeout=120)
    if result.returncode:
        raise RuntimeError("C++ build failed:\\n" + (result.stderr or result.stdout)[-4000:])
    return str(BINARY)

def pack_to_blob(file_paths, blob_path, manifest_path):
    files = [str(Path(p).resolve()) for p in file_paths if Path(p).is_file()]
    if not files:
        raise ValueError("Select at least one existing file to pack.")
    binary = compile_engine()
    blob = Path(blob_path).resolve(); manifest = Path(manifest_path).resolve()
    blob.parent.mkdir(parents=True, exist_ok=True); manifest.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run([binary, "pack", str(blob), str(manifest), *files],
                            capture_output=True, text=True, timeout=600)
    if result.returncode:
        raise RuntimeError("C++ pack failed:\\n" + (result.stderr or result.stdout)[-4000:])
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
                conn.execute("""INSERT INTO blob_assets(source_path,blob_path,manifest_path,byte_offset,payload_size,is_duplicate)
                    VALUES(?,?,?,?,?,?)
                    ON CONFLICT(source_path,blob_path) DO UPDATE SET manifest_path=excluded.manifest_path,
                    byte_offset=excluded.byte_offset,payload_size=excluded.payload_size,is_duplicate=excluded.is_duplicate,
                    packed_at=CURRENT_TIMESTAMP""",
                    (source, str(blob), str(manifest), int(row["byte_offset"]), int(row["payload_size"]), int(row["is_duplicate"])))
                imported += 1
        conn.execute("INSERT INTO audit_log(event_type,detail) VALUES(?,?)",
                     ("cpp_blob_pack", f"blob={blob}; manifest={manifest}; imported={imported}"))
    return {"blob_path":str(blob),"manifest_path":str(manifest),"manifest_rows":imported,
            "stdout":result.stdout}

def extract_from_blob(blob_path, offset, output_path):
    binary = compile_engine()
    result = subprocess.run([binary,"extract",str(Path(blob_path).resolve()),str(int(offset)),
                             str(Path(output_path).resolve())],capture_output=True,text=True,timeout=120)
    if result.returncode:
        raise RuntimeError((result.stderr or result.stdout)[-3000:])
    return result.stdout
