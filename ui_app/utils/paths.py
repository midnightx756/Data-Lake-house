from pathlib import Path
SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".idea"}
def iter_files(folder):
    root = Path(folder).expanduser().resolve()
    if not root.is_dir(): raise NotADirectoryError(str(root))
    for path in root.rglob("*"):
        if any(part in SKIP_DIRS for part in path.parts): continue
        if path.is_file(): yield path
