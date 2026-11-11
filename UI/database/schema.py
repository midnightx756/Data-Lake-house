def create_schema(conn):
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS assets(
      asset_id INTEGER PRIMARY KEY AUTOINCREMENT,
      path TEXT NOT NULL UNIQUE,
      name TEXT NOT NULL,
      extension TEXT,
      mime_type TEXT,
      size_bytes INTEGER NOT NULL DEFAULT 0,
      modified_at REAL,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP,
      sha256 TEXT,
      is_duplicate INTEGER NOT NULL DEFAULT 0,
      extracted_text TEXT DEFAULT '',
      status TEXT NOT NULL DEFAULT 'indexed'
    );
    CREATE INDEX IF NOT EXISTS idx_assets_name ON assets(name);
    CREATE INDEX IF NOT EXISTS idx_assets_extension ON assets(extension);
    CREATE INDEX IF NOT EXISTS idx_assets_hash ON assets(sha256);
    CREATE INDEX IF NOT EXISTS idx_assets_size ON assets(size_bytes);
    CREATE TABLE IF NOT EXISTS jobs(
      job_id INTEGER PRIMARY KEY AUTOINCREMENT,
      kind TEXT NOT NULL, target TEXT, status TEXT NOT NULL,
      started_at TEXT, finished_at TEXT, scanned INTEGER DEFAULT 0,
      inserted INTEGER DEFAULT 0, duplicates INTEGER DEFAULT 0,
      errors INTEGER DEFAULT 0, message TEXT DEFAULT ''
    );
    CREATE TABLE IF NOT EXISTS audit_log(
      event_id INTEGER PRIMARY KEY AUTOINCREMENT,
      event_type TEXT NOT NULL, detail TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)
