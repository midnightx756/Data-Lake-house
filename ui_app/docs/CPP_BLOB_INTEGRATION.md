# C++ blob integration

The Storage view compiles `cpp_engine/sdlh_blob.cpp` with a local C++17 compiler,
packs chosen files into a new binary blob, writes a CSV manifest and imports each
source path, blob path, byte offset, payload size and duplicate flag into SQLite.
The packer uses a 64-byte SDLH header. Duplicate payloads point to the first matching
payload offset in the manifest and are not written a second time.

Windows setup: install MinGW-w64 or another C++17 compiler and make `g++` available
in PATH, then restart VS Code. Verify with `g++ --version`. If no compiler is found,
the Storage view shows an actionable error; other Python UI modules continue to work.

Safety: the integration creates a new `.blob` and manifest; it does not delete or
modify source files. Use a small sample set first. Duplicate matching in this starter
implementation compares payload bytes in memory; it is suitable for a demonstration,
not for very large individual files or huge input batches. SHA-256 in the Python
metadata scanner remains the stronger cryptographic integrity fingerprint.
