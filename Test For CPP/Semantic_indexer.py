#Document #1: Alpha version dataset specifications.

import os
import csv
import sqlite3
import numpy as np
from PIL import Image
from sentence_transformers import SentenceTransformer

# ==============================================================================
# CONFIGURATION
# ==============================================================================
MODEL_NAME = "clip-ViT-B-32"
DB_NAME = "sdlh_metadata.db"

print(f"[INIT] Loading CLIP Model '{MODEL_NAME}'... (This takes a moment on first run)")
model = SentenceTransformer(MODEL_NAME)
print("[INIT] Model loaded successfully!\n")

# ==============================================================================
# 1. DATABASE INITIALIZATION
# ==============================================================================
def init_db(db_path=DB_NAME):
    """Creates the SQLite metadata table with byte-offset and embedding storage."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assets (
            asset_id INTEGER PRIMARY KEY,
            original_name TEXT NOT NULL,
            content_hash TEXT NOT NULL,
            byte_offset INTEGER NOT NULL,
            payload_size INTEGER NOT NULL,
            is_duplicate INTEGER NOT NULL,
            embedding BLOB
        )
    """)
    conn.commit()
    conn.close()
    print(f"[DB] Initialized SQLite schema in '{db_path}'")

# ==============================================================================
# 2. INGESTION & EMBEDDING PIPELINE
# ==============================================================================
def index_dataset(manifest_csv, assets_dir, db_path=DB_NAME):
    """
    Reads the C++ manifest.csv, computes CLIP embeddings for non-duplicate images,
    and inserts records with exact physical byte offsets into SQLite.
    """
    if not os.path.exists(manifest_csv):
        print(f"[ERROR] Manifest file not found: {manifest_csv}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    with open(manifest_csv, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            asset_id = int(row["asset_id"])
            name = row["original_name"]
            content_hash = row["content_hash"]
            offset = int(row["byte_offset"])
            size = int(row["payload_size"])
            is_dup = int(row["is_duplicate"])

            embedding_blob = None
            file_path = os.path.join(assets_dir, name)

            # Only compute embeddings for valid image files
            if os.path.exists(file_path) and name.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.webp')):
                try:
                    img = Image.open(file_path).convert("RGB")
                    # Generate 512-D float32 vector
                    vector = model.encode(img, normalize_embeddings=True)
                    embedding_blob = vector.astype(np.float32).tobytes()
                except Exception as e:
                    print(f"[WARN] Failed to generate embedding for {name}: {e}")

            # Insert into SQLite
            cursor.execute("""
                INSERT OR REPLACE INTO assets 
                (asset_id, original_name, content_hash, byte_offset, payload_size, is_duplicate, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (asset_id, name, content_hash, offset, size, is_dup, embedding_blob))

            print(f"[INDEXED] Asset ID {asset_id}: {name} (Offset: {offset}, Size: {size})")

    conn.commit()
    conn.close()
    print("[DB] Dataset successfully indexed into SQLite!")

# ==============================================================================
# 3. SEMANTIC SEARCH FUNCTION
# ==============================================================================
def search_by_text(query_text, db_path=DB_NAME, top_k=5):
    """Encodes query text into a vector and finds the most similar assets via Cosine Similarity."""
    print(f"\n[SEARCH] Searching for query: '{query_text}'...")
    
    query_vector = model.encode(query_text, normalize_embeddings=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT asset_id, original_name, byte_offset, payload_size, embedding FROM assets WHERE embedding IS NOT NULL")
    rows = cursor.fetchall()
    
    results = []
    for row in rows:
        asset_id, name, offset, size, emb_blob = row
        stored_vector = np.frombuffer(emb_blob, dtype=np.float32)
        
        # Calculate Cosine Similarity (since vectors are normalized, dot product = cosine similarity)
        similarity = np.dot(query_vector, stored_vector)
        results.append((similarity, asset_id, name, offset, size))
        
    # Sort by highest similarity score
    results.sort(key=lambda x: x[0], reverse=True)
    
    print(f"\nTop {top_k} Results:")
    print("-" * 65)
    for score, asset_id, name, offset, size in results[:top_k]:
        print(f"Score: {score:.4f} | ID: {asset_id} | File: {name} | Offset: {offset}")
    print("-" * 65)
    
    conn.close()
    return results[:top_k]

# ==============================================================================
# MAIN EXECUTION DEMO
# ==============================================================================
if __name__ == "__main__":
    # Initialize Database Schema
    init_db()
    
    # Example usage placeholder (Point to your actual manifest.csv and assets folder)
    # manifest_path = "manifest.csv"
    # assets_dir = "./raw_assets"
    # index_dataset(manifest_path, assets_dir)
    
    # Example search test
    # search_by_text("a photo of a cat")
