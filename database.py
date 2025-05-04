import sqlite3
import os
import json
from datetime import datetime

DB_PATH = "conversations.db"

def init_db():
    """Veritabanını başlat ve gerekli tabloları oluştur"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Mesaj tablosu oluştur
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        character TEXT NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        timestamp TEXT NOT NULL
    )
    ''')
    
    conn.commit()
    conn.close()

def save_message(session_id, character, role, content):
    """Mesajı veritabanına kaydet
    
    Args:
        session_id (str): Konuşma oturumu ID'si
        character (str): Seçilen karakter (cocuk, universiteli, hoca)
        role (str): Mesajı gönderen (user/ai)
        content (str): Mesaj içeriği
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    timestamp = datetime.now().isoformat()
    
    cursor.execute(
        "INSERT INTO messages (session_id, character, role, content, timestamp) VALUES (?, ?, ?, ?, ?)",
        (session_id, character, role, content, timestamp)
    )
    
    conn.commit()
    conn.close()

def get_conversation(session_id):
    """Belirli bir oturum için konuşma geçmişini getir"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT role, content FROM messages WHERE session_id = ? ORDER BY timestamp ASC",
            (session_id,)
        )
        
        messages = cursor.fetchall()
        conn.close()
        
        # Son 10 mesaj ile sınırla (token limiti aşmamak için)
        if len(messages) > 10:
            messages = messages[-10:]
        
        # Gemini API formatında geçmiş oluştur
        history = []
        for role, content in messages:
            # Gemini API'nin beklediği format
            gemini_role = "user" if role == "user" else "model"
            history.append({"role": gemini_role, "parts": [{"text": content}]})
        
        return history
    except Exception as e:
        print(f"Konuşma geçmişi alınırken hata: {str(e)}")
        return []  # Hata durumunda boş liste döndür