"""SQLite Store - Persistência por chat (histórico até limpeza pelo usuário)"""
import sqlite3
import json
import os
from typing import List, Dict, Optional

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
                chat_id INTEGER,
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
        try:
            conn.execute("ALTER TABLE conversations ADD COLUMN chat_id INTEGER")
        except sqlite3.OperationalError:
            pass
        conn.commit()
        conn.close()

    def add_message(self, role: str, content: str, chat_id: Optional[int] = None):
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT INTO conversations (chat_id, role, content) VALUES (?, ?, ?)",
            (chat_id, role, content),
        )
        conn.commit()
        conn.close()

    def get_history(self, limit: int = 20, chat_id: Optional[int] = None) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        if chat_id is not None:
            cursor = conn.execute(
                "SELECT role, content FROM conversations WHERE chat_id = ? ORDER BY id DESC LIMIT ?",
                (chat_id, limit),
            )
        else:
            cursor = conn.execute(
                "SELECT role, content FROM conversations WHERE chat_id IS NULL ORDER BY id DESC LIMIT ?",
                (limit,),
            )
        messages = [{"role": row[0], "content": row[1]} for row in cursor.fetchall()]
        conn.close()
        return list(reversed(messages))

    def clear_history(self, chat_id: Optional[int] = None):
        conn = sqlite3.connect(self.db_path)
        if chat_id is not None:
            conn.execute("DELETE FROM conversations WHERE chat_id = ?", (chat_id,))
        else:
            conn.execute("DELETE FROM conversations WHERE chat_id IS NULL")
        conn.commit()
        conn.close()

    def log_metric(self, event: str, data: Dict = None):
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT INTO metrics (event, data) VALUES (?, ?)",
            (event, json.dumps(data) if data else None),
        )
        conn.commit()
        conn.close()
