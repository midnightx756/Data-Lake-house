# Architecture

Tkinter UI -> service layer -> core processing -> SQLite repositories.
The scanner enumerates a selected folder, computes chunked SHA-256, extracts basic
metadata and supported text, then writes rows to SQLite. A single background worker
prevents long scans from running in the UI thread. WAL mode and indexes improve local
read/write behavior. This is a laptop-scale prototype, not a distributed lakehouse.
