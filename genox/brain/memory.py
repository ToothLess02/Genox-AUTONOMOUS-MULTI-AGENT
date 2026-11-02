import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from genox.config import DB_PATH

class MemoryManager:
    def __init__(self, db_path=DB_PATH):
        self.db_path = str(db_path)
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Key-value episodic & semantic facts
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE,
                    value TEXT NOT NULL,
                    category TEXT DEFAULT 'general',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Task execution logs
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS task_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prompt TEXT NOT NULL,
                    final_response TEXT,
                    steps TEXT,
                    success INTEGER DEFAULT 1,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def save_memory(self, key: str, value: str, category: str = "general") -> str:
        """Save or update a memory fact (e.g. user preferences, project notes)."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO memories (key, value, category, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    category = excluded.category,
                    updated_at = CURRENT_TIMESTAMP
            """, (key.strip(), value.strip(), category.strip()))
            conn.commit()
            return f"Successfully remembered: '{key}'"

    def recall_memory(self, query: str = "") -> List[Dict[str, Any]]:
        """Recall memories matching a keyword or return top memories."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if query.strip():
                like_pattern = f"%{query.strip()}%"
                cursor.execute("""
                    SELECT key, value, category, updated_at FROM memories
                    WHERE key LIKE ? OR value LIKE ? OR category LIKE ?
                    ORDER BY updated_at DESC LIMIT 20
                """, (like_pattern, like_pattern, like_pattern))
            else:
                cursor.execute("""
                    SELECT key, value, category, updated_at FROM memories
                    ORDER BY updated_at DESC LIMIT 20
                """)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def delete_memory(self, key: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM memories WHERE key = ?", (key.strip(),))
            conn.commit()
            return cursor.rowcount > 0

    def log_task(self, prompt: str, final_response: str, steps: List[Dict[str, Any]], success: bool = True):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO task_history (prompt, final_response, steps, success)
                VALUES (?, ?, ?, ?)
            """, (prompt, final_response, json.dumps(steps, default=str), 1 if success else 0))
            conn.commit()

    def get_recent_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, prompt, final_response, steps, success, timestamp 
                FROM task_history ORDER BY id DESC LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            results = []
            for r in rows:
                item = dict(r)
                try:
                    item['steps'] = json.loads(item['steps'])
                except Exception:
                    pass
                results.append(item)
            return results

# Singleton instance
memory = MemoryManager()
