# Divyam - AI & Integrity Lead (individual files only)

This ZIP contains only the files added for the AI & Integrity Lead contribution in the generated integrated project. It does NOT include Taru's database/UI base project or Graahil's original C++ storage implementation.

## Files
- `core/semantic_search.py` - CLIP image indexing and text-to-image semantic search.
- `core/blob_integrity.py` - checks blob asset headers, payload sizes and SHA-256 hashes against SQLite metadata.
- `core/cpp_blob_bridge.py` - Python wrapper for compiling/running the project's C++ blob engine.
- `services/integrity_service.py` - connects integrity functions to the app.
- `ui/search_view.py` - search screen additions for CLIP indexing/search.
- `ui/integrity_view.py` - integrity screen additions.
- `tests/test_blob_integrity.py` - tests for blob integrity checking.

## Important
These are individual contribution files, not a standalone runnable application. They import modules from the shared SDLH project (for example `database.connection`, `ui.widgets`, and `config`). To run them, copy the files into the matching folders of the full integrated project and keep the shared project files in place.

CLIP dependencies: `pip install sentence-transformers numpy pillow`. The first CLIP model use may download `clip-ViT-B-32`.

The code has not been verified end-to-end on your Mac.
