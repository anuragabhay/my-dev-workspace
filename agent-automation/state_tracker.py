"""
State Tracker - Manages processed approvals, tasks, and trigger history.
Uses SQLite as primary storage with JSON backup.
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path


class StateTracker:
    """Tracks processed items to prevent duplicate triggers."""
    
    def __init__(self, db_path: str, json_backup_path: str):
        self.db_path = db_path
        self.json_backup_path = json_backup_path
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database with required tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Processed approvals table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS processed_approvals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                approval_id TEXT UNIQUE NOT NULL,
                role TEXT NOT NULL,
                status TEXT NOT NULL,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                trigger_count INTEGER DEFAULT 1
            )
        """)
        
        # Trigger history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trigger_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                trigger_type TEXT NOT NULL,
                item_id TEXT,
                prompt_file TEXT,
                triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'pending'
            )
        """)
        
        # Processed tasks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS processed_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_hash TEXT UNIQUE NOT NULL,
                role TEXT NOT NULL,
                task_description TEXT,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Last check timestamp
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS last_check (
                id INTEGER PRIMARY KEY,
                last_check_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def is_approval_processed(self, approval_id: str) -> bool:
        """Check if an approval has already been processed."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM processed_approvals WHERE approval_id = ?",
            (approval_id,)
        )
        result = cursor.fetchone()
        conn.close()
        return result is not None
    
    def mark_approval_processed(self, approval_id: str, role: str, status: str = "triggered"):
        """Mark an approval as processed."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if already exists
        cursor.execute(
            "SELECT trigger_count FROM processed_approvals WHERE approval_id = ?",
            (approval_id,)
        )
        existing = cursor.fetchone()
        
        if existing:
            # Increment trigger count
            cursor.execute(
                "UPDATE processed_approvals SET trigger_count = trigger_count + 1, processed_at = CURRENT_TIMESTAMP WHERE approval_id = ?",
                (approval_id,)
            )
        else:
            # Insert new record
            cursor.execute(
                "INSERT INTO processed_approvals (approval_id, role, status) VALUES (?, ?, ?)",
                (approval_id, role, status)
            )
        
        conn.commit()
        conn.close()
        self._backup_to_json()
    
    def log_trigger(self, role: str, trigger_type: str, item_id: Optional[str] = None, prompt_file: Optional[str] = None):
        """Log a trigger event."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO trigger_history (role, trigger_type, item_id, prompt_file) 
               VALUES (?, ?, ?, ?)""",
            (role, trigger_type, item_id, prompt_file)
        )
        conn.commit()
        conn.close()
        self._backup_to_json()
    
    def update_trigger_status(self, trigger_id: int, status: str):
        """Update trigger status (e.g., 'completed', 'failed')."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE trigger_history SET status = ? WHERE id = ?",
            (status, trigger_id)
        )
        conn.commit()
        conn.close()
        self._backup_to_json()
    
    def is_task_processed(self, task_hash: str) -> bool:
        """Check if a task has already been processed."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM processed_tasks WHERE task_hash = ?",
            (task_hash,)
        )
        result = cursor.fetchone()
        conn.close()
        return result is not None
    
    def mark_task_processed(self, task_hash: str, role: str, task_description: str = ""):
        """Mark a task as processed."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO processed_tasks (task_hash, role, task_description) VALUES (?, ?, ?)",
            (task_hash, role, task_description)
        )
        conn.commit()
        conn.close()
        self._backup_to_json()
    
    def update_last_check(self):
        """Update the last check timestamp."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM last_check")
        cursor.execute("INSERT INTO last_check (id) VALUES (1)")
        conn.commit()
        conn.close()
    
    def get_last_check_time(self) -> Optional[datetime]:
        """Get the last check timestamp."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT last_check_time FROM last_check WHERE id = 1")
        result = cursor.fetchone()
        conn.close()
        if result:
            return datetime.fromisoformat(result[0])
        return None
    
    def get_recent_triggers(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent trigger history."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id, role, trigger_type, item_id, prompt_file, triggered_at, status 
               FROM trigger_history 
               ORDER BY triggered_at DESC 
               LIMIT ?""",
            (limit,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": row[0],
                "role": row[1],
                "trigger_type": row[2],
                "item_id": row[3],
                "prompt_file": row[4],
                "triggered_at": row[5],
                "status": row[6]
            }
            for row in rows
        ]
    
    def _backup_to_json(self):
        """Backup state to JSON file."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Export processed approvals
            cursor.execute("SELECT * FROM processed_approvals")
            approvals = [
                {
                    "id": row[0],
                    "approval_id": row[1],
                    "role": row[2],
                    "status": row[3],
                    "processed_at": row[4],
                    "trigger_count": row[5]
                }
                for row in cursor.fetchall()
            ]
            
            # Export trigger history
            cursor.execute("SELECT * FROM trigger_history ORDER BY triggered_at DESC LIMIT 100")
            triggers = [
                {
                    "id": row[0],
                    "role": row[1],
                    "trigger_type": row[2],
                    "item_id": row[3],
                    "prompt_file": row[4],
                    "triggered_at": row[5],
                    "status": row[6]
                }
                for row in cursor.fetchall()
            ]
            
            # Export processed tasks
            cursor.execute("SELECT * FROM processed_tasks")
            tasks = [
                {
                    "id": row[0],
                    "task_hash": row[1],
                    "role": row[2],
                    "task_description": row[3],
                    "processed_at": row[4]
                }
                for row in cursor.fetchall()
            ]
            
            conn.close()
            
            backup_data = {
                "last_backup": datetime.now().isoformat(),
                "processed_approvals": approvals,
                "trigger_history": triggers,
                "processed_tasks": tasks
            }
            
            with open(self.json_backup_path, 'w') as f:
                json.dump(backup_data, f, indent=2)
        
        except Exception as e:
            # Log error but don't fail
            print(f"Warning: Failed to backup to JSON: {e}")

