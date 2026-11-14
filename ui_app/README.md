# Semantic Data Lakehouse (SDLH) — Tkinter Integrated Edition

Third-year BTech CSE project integrating metadata management, data ingestion,
SQLite/DBMS concepts, OS-style background jobs, integrity checks, deduplication,
a simple searchable metadata/text index, and an optional C++ storage core.

## Run (Windows)
1. Install Python 3.10+.
2. Extract this ZIP and open the `SDLH_Integrated_Tkinter` folder in VS Code.
3. In the terminal: `python -m pip install -r requirements.txt`
4. Run: `python main.py`

The desktop interface is built with Tkinter/ttk, not Flask. The core works CPU-only.
Use **Scan Folder** to index a test directory. SQLite stores metadata; source files
remain in place. Use a copied sample dataset first.

## C++ core
Original C++ sources from the `devtest` branch are retained in `legacy_branches/devtest`.
The Python application does not silently assume a C++ shared library is compatible.
Build and validate the CLI separately using its included Makefile in that snapshot
(Linux/WSL with g++); integration with Python is an optional next milestone.

## AI / semantic search
The Search page has an **Index Images with CLIP** button. Install the optional
packages first with `python -m pip install sentence-transformers numpy`.
The first run downloads the `clip-ViT-B-32` model. Indexing stores image vectors
in the SQLite `asset_embeddings` table. After indexing, search with ordinary text.
If no vectors exist yet, the app keeps its basic keyword search available.

## Integrity work
The Integrity page can check both original files and packed blob records.
The blob check validates the 64-byte SDLH header, payload size and payload hash
against the SHA-256 value recorded when the original file was scanned.

## Project modules
- UI: Dashboard, Explorer, Ingestion, Search, DBMS, Integrity, Benchmark, Settings
- Core: scanner, chunked SHA-256, metadata extraction, deduplication, job queue
- DBMS: normalized SQLite tables, indexes, transactions, repository methods
- Analytics: local synthetic benchmark
- Tests: schema, scanner, and search tests

## Limitations
- SQLite is suitable for a laptop-scale demonstrator; a million records needs indexing,
  batch ingestion, disk-space planning, and benchmark evidence on the target machine.
- Job queue is in-process; pending jobs do not survive an application restart.
- Full distributed storage, production security, and vector embeddings are not claimed
  as implemented.


## UI theme update
The desktop UI uses a dark navy theme with yellow accents and a refreshed sidebar, overview cards and file-type table. Restart the application after updating.


## C++ Blob Storage integration
Open **Storage**, choose a few files, choose a new `.blob` path, and the app invokes the portable C++17 packer. It writes a manifest and imports source/blob offsets into SQLite. Requires `g++` or `clang++` on PATH. Original files are never deleted. See `docs/CPP_BLOB_INTEGRATION.md`.
