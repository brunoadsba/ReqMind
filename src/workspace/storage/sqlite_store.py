"""SQLite Store - Persistência simples"""
import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict

class SQLiteStore:
    def __init__(self, db_path: str = "~/.moltbot/moltbot.db"):
        self.db_path = os.path.expanduser(db_path)
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event TEXT NOT NULL,
                data TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
    
    def add_message(self, role: str, content: str):
        conn = sqlite3.connect(self.db_path)
        conn.execute("INSERT INTO conversations (role, content) VALUES (?, ?)", (role, content))
        conn.commit()
        conn.close()
    
    def get_history(self, limit: int = 20) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("SELECT role, content FROM conversations ORDER BY id DESC LIMIT ?", (limit,))
        messages = [{"role": row[0], "content": row[1]} for row in cursor.fetchall()]
        conn.close()
        return list(reversed(messages))
    
    def clear_history(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM conversations")
        conn.commit()
        conn.close()
    
    def log_metric(self, event: str, data: Dict = None):
        conn = sqlite3.connect(self.db_path)
        conn.execute("INSERT INTO metrics (event, data) VALUES (?, ?)", (event, json.dumps(data) if data else None))
        conn.commit()
        conn.close()
