"""
OfflineQueue: Stores deltas for offline sync (IndexedDB for web, SQLite for desktop)
"""
import os
import sqlite3
from typing import List, Dict, Any

class OfflineQueue:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or os.path.expanduser("~/.offline_queue.db")
        self._init_db()

    def _init_db(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute('''CREATE TABLE IF NOT EXISTS deltas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_id TEXT,
            delta_type TEXT,
            delta BLOB,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')
        self.conn.commit()

    def add_delta(self, doc_id: str, delta_type: str, delta: bytes):
        self.conn.execute(
            "INSERT INTO deltas (doc_id, delta_type, delta) VALUES (?, ?, ?)",
            (doc_id, delta_type, delta)
        )
        self.conn.commit()

    def get_deltas(self, doc_id: str) -> List[Dict[str, Any]]:
        cur = self.conn.execute(
            "SELECT id, delta_type, delta, timestamp FROM deltas WHERE doc_id = ? ORDER BY id ASC",
            (doc_id,)
        )
        return [
            {"id": row[0], "delta_type": row[1], "delta": row[2], "timestamp": row[3]}
            for row in cur.fetchall()
        ]

    def remove_delta(self, delta_id: int):
        self.conn.execute("DELETE FROM deltas WHERE id = ?", (delta_id,))
        self.conn.commit()
