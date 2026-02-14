"""
Data access layer for SQLite. Uses schema from migrations; models define row shapes.
"""
import sqlite3
import json
from pathlib import Path
from typing import Optional, List, Any

from .migrations import DEFAULT_DB, run_migrations, _project_root
from . import models


def _get_conn(db_path: Optional[Path] = None) -> sqlite3.Connection:
    path = db_path or _project_root() / DEFAULT_DB
    return sqlite3.connect(str(path))


def ensure_schema(db_path: Optional[Path] = None) -> None:
    """Run migrations if needed."""
    run_migrations(db_path)


# --- Executions ---

def create_execution(
    status: str = models.STATUS_PENDING,
    start_time: Optional[str] = None,
    current_stage: Optional[str] = None,
    db_path: Optional[Path] = None,
) -> int:
    ensure_schema(db_path)
    conn = _get_conn(db_path)
    try:
        cur = conn.execute(
            "INSERT INTO executions (status, start_time, current_stage) VALUES (?, ?, ?)",
            (status, start_time or None, current_stage),
        )
        conn.commit()
        return cur.lastrowid or 0
    finally:
        conn.close()


def update_execution(
    execution_id: int,
    status: Optional[str] = None,
    end_time: Optional[str] = None,
    current_stage: Optional[str] = None,
    error_message: Optional[str] = None,
    cost_total: Optional[float] = None,
    db_path: Optional[Path] = None,
) -> None:
    conn = _get_conn(db_path)
    try:
        updates = []
        args = []
        if status is not None:
            updates.append("status = ?")
            args.append(status)
        if end_time is not None:
            updates.append("end_time = ?")
            args.append(end_time)
        if current_stage is not None:
            updates.append("current_stage = ?")
            args.append(current_stage)
        if error_message is not None:
            updates.append("error_message = ?")
            args.append(error_message)
        if cost_total is not None:
            updates.append("cost_total = ?")
            args.append(cost_total)
        if not updates:
            return
        args.append(execution_id)
        conn.execute(
            f"UPDATE executions SET {', '.join(updates)} WHERE id = ?",
            args,
        )
        conn.commit()
    finally:
        conn.close()


def get_execution(execution_id: int, db_path: Optional[Path] = None) -> Optional[dict]:
    """Get one execution by id."""
    ensure_schema(db_path)
    conn = _get_conn(db_path)
    try:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM executions WHERE id = ?", (execution_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_last_executions(n: int = 10, db_path: Optional[Path] = None) -> List[dict]:
    ensure_schema(db_path)
    conn = _get_conn(db_path)
    try:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM executions ORDER BY id DESC LIMIT ?",
            (n,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# --- Costs ---

def get_execution_cost_total(execution_id: int, db_path: Optional[Path] = None) -> float:
    """Sum costs for an execution."""
    ensure_schema(db_path)
    conn = _get_conn(db_path)
    try:
        row = conn.execute(
            "SELECT COALESCE(SUM(cost), 0) FROM costs WHERE execution_id = ?",
            (execution_id,),
        ).fetchone()
        return float(row[0]) if row else 0.0
    finally:
        conn.close()


def insert_cost(
    execution_id: int,
    component: str,
    cost: float,
    timestamp: Optional[str] = None,
    db_path: Optional[Path] = None,
) -> int:
    import datetime
    ts = timestamp or datetime.datetime.utcnow().isoformat() + "Z"
    ensure_schema(db_path)
    conn = _get_conn(db_path)
    try:
        cur = conn.execute(
            "INSERT INTO costs (execution_id, component, cost, timestamp) VALUES (?, ?, ?, ?)",
            (execution_id, component, cost, ts),
        )
        conn.commit()
        return cur.lastrowid or 0
    finally:
        conn.close()


# --- Videos ---

def insert_video(
    execution_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    youtube_id: Optional[str] = None,
    publish_date: Optional[str] = None,
    script_text: Optional[str] = None,
    db_path: Optional[Path] = None,
) -> int:
    ensure_schema(db_path)
    conn = _get_conn(db_path)
    try:
        cur = conn.execute(
            """INSERT INTO videos (execution_id, title, description, youtube_id, publish_date, script_text)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (execution_id, title, description, youtube_id, publish_date, script_text),
        )
        conn.commit()
        return cur.lastrowid or 0
    finally:
        conn.close()


def get_video_by_youtube_id(youtube_id: str, db_path: Optional[Path] = None) -> Optional[dict]:
    ensure_schema(db_path)
    conn = _get_conn(db_path)
    try:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM videos WHERE youtube_id = ?", (youtube_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


# --- Embeddings ---

def insert_embedding(
    video_id: int,
    embedding_vector: bytes,
    created_at: Optional[str] = None,
    db_path: Optional[Path] = None,
) -> int:
    import datetime
    ts = created_at or datetime.datetime.utcnow().isoformat() + "Z"
    ensure_schema(db_path)
    conn = _get_conn(db_path)
    try:
        cur = conn.execute(
            "INSERT INTO embeddings (video_id, embedding_vector, created_at) VALUES (?, ?, ?)",
            (video_id, embedding_vector, ts),
        )
        conn.commit()
        return cur.lastrowid or 0
    finally:
        conn.close()


def get_embeddings_for_videos(video_ids: List[int], db_path: Optional[Path] = None) -> List[dict]:
    if not video_ids:
        return []
    ensure_schema(db_path)
    conn = _get_conn(db_path)
    try:
        conn.row_factory = sqlite3.Row
        placeholders = ",".join("?" * len(video_ids))
        rows = conn.execute(
            f"SELECT * FROM embeddings WHERE video_id IN ({placeholders}) ORDER BY created_at DESC",
            video_ids,
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# --- Message queue ---

def enqueue(
    from_agent: str,
    to_agent: str,
    message_type: str,
    payload: Optional[str] = None,
    status: str = models.QUEUE_PENDING,
    db_path: Optional[Path] = None,
) -> int:
    import datetime
    ts = datetime.datetime.utcnow().isoformat() + "Z"
    ensure_schema(db_path)
    conn = _get_conn(db_path)
    try:
        cur = conn.execute(
            """INSERT INTO message_queue (from_agent, to_agent, message_type, payload, status, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (from_agent, to_agent, message_type, payload or "", status, ts),
        )
        conn.commit()
        return cur.lastrowid or 0
    finally:
        conn.close()


def dequeue_next(to_agent: Optional[str] = None, db_path: Optional[Path] = None) -> Optional[dict]:
    """Get next pending message for to_agent (or any if to_agent is None); mark as processing."""
    ensure_schema(db_path)
    conn = _get_conn(db_path)
    try:
        conn.row_factory = sqlite3.Row
        if to_agent:
            row = conn.execute(
                "SELECT * FROM message_queue WHERE status = ? AND to_agent = ? ORDER BY id LIMIT 1",
                (models.QUEUE_PENDING, to_agent),
            ).fetchone()
        else:
            row = conn.execute(
                "SELECT * FROM message_queue WHERE status = ? ORDER BY id LIMIT 1",
                (models.QUEUE_PENDING,),
            ).fetchone()
        if not row:
            return None
        msg_id = row["id"]
        conn.execute(
            "UPDATE message_queue SET status = ? WHERE id = ?",
            (models.QUEUE_PROCESSING, msg_id),
        )
        conn.commit()
        return dict(row)
    finally:
        conn.close()


def mark_message_processed(
    message_id: int,
    status: str = models.QUEUE_COMPLETED,
    db_path: Optional[Path] = None,
) -> None:
    """Set message status and processed_at."""
    import datetime
    ts = datetime.datetime.utcnow().isoformat() + "Z"
    conn = _get_conn(db_path)
    try:
        conn.execute(
            "UPDATE message_queue SET status = ?, processed_at = ? WHERE id = ?",
            (status, ts, message_id),
        )
        conn.commit()
    finally:
        conn.close()
