import sqlite3
from pathlib import Path

DB_PATH = "log.db"

def init_db():
    """Veritabanı dosyası ve logs tablosu yoksa oluşturur."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            character TEXT NOT NULL,
            topic TEXT NOT NULL,
            prompt TEXT NOT NULL,
            response TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def log_request(character: str, topic: str, prompt: str, response: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO logs (character, topic, prompt, response)
        VALUES (?, ?, ?, ?)
    """, (character, topic, prompt, response))
    conn.commit()
    conn.close()

