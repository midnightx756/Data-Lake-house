"""Simple CLIP image indexing and semantic search for SDLH."""
import sqlite3
import numpy as np
from PIL import Image

from database.connection import get_connection
from core.search import search_assets

MODEL_NAME = "clip-ViT-B-32"
_model = None


def get_model():
    """Load the CLIP model only when it is first needed."""
    global _model

    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise RuntimeError(
                "CLIP needs sentence-transformers. Install it with: "
                "pip install sentence-transformers"
            )

        _model = SentenceTransformer(MODEL_NAME)

    return _model


def create_embedding_table():
    """Create a small table for image vectors."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS asset_embeddings (
                asset_id INTEGER PRIMARY KEY,
                embedding BLOB NOT NULL
            )
        """)


def index_images():
    """Create and save one CLIP vector for each image in the asset database."""
    create_embedding_table()
    model = get_model()
    indexed = 0
    skipped = 0

    with get_connection() as conn:
        assets = conn.execute(
            "SELECT asset_id, path FROM assets ORDER BY asset_id"
        ).fetchall()

        for asset in assets:
            try:
                image = Image.open(asset["path"]).convert("RGB")
                vector = model.encode(image, normalize_embeddings=True)
                vector = np.asarray(vector, dtype=np.float32)

                conn.execute(
                    "INSERT OR REPLACE INTO asset_embeddings "
                    "(asset_id, embedding) VALUES (?, ?)",
                    (asset["asset_id"], vector.tobytes())
                )
                indexed += 1
            except Exception:
                # Text files and unreadable images are skipped.
                skipped += 1

    return {"indexed": indexed, "skipped": skipped}


def semantic_search(query, limit=100):
    """Find images closest to the text query using cosine similarity."""
    if not query.strip():
        return []

    create_embedding_table()
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT a.asset_id, a.name, a.extension, a.path, e.embedding
            FROM assets AS a
            JOIN asset_embeddings AS e ON a.asset_id = e.asset_id
        """).fetchall()

    # If CLIP has not been run yet, keep the old keyword search available.
    if not rows:
        return search_assets(query, limit=limit)

    model = get_model()
    query_vector = model.encode(query, normalize_embeddings=True)
    query_vector = np.asarray(query_vector, dtype=np.float32)

    results = []
    for row in rows:
        image_vector = np.frombuffer(row["embedding"], dtype=np.float32)

        if image_vector.shape != query_vector.shape:
            continue

        score = float(np.dot(query_vector, image_vector))
        results.append({
            "asset_id": row["asset_id"],
            "name": row["name"],
            "extension": row["extension"],
            "path": row["path"],
            "score": score
        })

    results.sort(key=lambda item: item["score"], reverse=True)
    return results[:max(1, int(limit))]
