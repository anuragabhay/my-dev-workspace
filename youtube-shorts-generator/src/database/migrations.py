"""
Schema initialization: create SQLite tables per approved architecture.
"""
import sqlite3
from pathlib import Path
from typing import Optional

# Default DB path (project root)
DEFAULT_DB = "youtube_shorts.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS executions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    status TEXT NOT NULL,
    start_time TEXT,
    end_time TEXT,
    current_stage TEXT,
    error_message TEXT,
    cost_total REAL
);

CREATE TABLE IF NOT EXISTS costs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    execution_id INTEGER NOT NULL,
    component TEXT NOT NULL,
    cost REAL NOT NULL,
    timestamp TEXT NOT NULL,
    FOREIGN KEY (execution_id) REFERENCES executions(id)
);

CREATE TABLE IF NOT EXISTS videos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    execution_id INTEGER NOT NULL,
    title TEXT,
    description TEXT,
    youtube_id TEXT,
    publish_date TEXT,
    script_text TEXT,
    FOREIGN KEY (execution_id) REFERENCES executions(id)
);

CREATE TABLE IF NOT EXISTS embeddings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id INTEGER NOT NULL,
    embedding_vector BLOB NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (video_id) REFERENCES videos(id)
);

CREATE TABLE IF NOT EXISTS message_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_agent TEXT NOT NULL,
    to_agent TEXT NOT NULL,
    message_type TEXT NOT NULL,
    payload TEXT,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    processed_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_costs_execution_id ON costs(execution_id);
CREATE INDEX IF NOT EXISTS idx_videos_execution_id ON videos(execution_id);
CREATE INDEX IF NOT EXISTS idx_videos_youtube_id ON videos(youtube_id);
CREATE INDEX IF NOT EXISTS idx_embeddings_video_id ON embeddings(video_id);
CREATE INDEX IF NOT EXISTS idx_message_queue_status ON message_queue(status);
"""


def _project_root() -> Path:
    here = Path(__file__).resolve().parent
    while here.name != "src" and here.parent != here:
        here = here.parent
    return here.parent if here.name == "src" else Path.cwd()


def run_migrations(db_path: Optional[Path] = None) -> None:
    """Create or update schema. Idempotent (IF NOT EXISTS)."""
    path = db_path or _project_root() / DEFAULT_DB
    path = Path(path)
    conn = sqlite3.connect(str(path))
    try:
        conn.executescript(SCHEMA)
        conn.commit()
    finally:
        conn.close()
