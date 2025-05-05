import sqlite3
import os
import json
from datetime import datetime
import bcrypt

DB_PATH = "conversations.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        session_id TEXT NOT NULL,
        character TEXT NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS session_scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        session_id TEXT NOT NULL,
        character TEXT NOT NULL,
        avg_score REAL NOT NULL,
        timestamp TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    ''')
    
    conn.commit()
    conn.close()

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        hashed_pw = hash_password(password)
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pw))
        conn.commit()
    except sqlite3.IntegrityError:
        raise Exception("Bu kullanıcı adı zaten alınmış.")
    finally:
        conn.close()

def get_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, password FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user and verify_password(password, user[1]):
        return user[0]  # user_id
    return None

def save_message(user_id, session_id, character, role, content):
    """Mesajı veritabanına kaydet"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    timestamp = datetime.now().isoformat()

    cursor.execute(
        "INSERT INTO messages (user_id, session_id, character, role, content, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, session_id, character, role, content, timestamp)
    )

    conn.commit()
    conn.close()


def get_conversation(user_id, session_id):
    """Belirli bir kullanıcı ve oturum için konuşma geçmişini getir"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT role, content FROM messages WHERE user_id = ? AND session_id = ? ORDER BY timestamp ASC",
            (user_id, session_id)
        )
        
        messages = cursor.fetchall()
        conn.close()
        
        # Son 10 mesaj ile sınırla (token limiti aşmamak için)
        if len(messages) > 10:
            messages = messages[-10:]
        
        # Gemini API formatında geçmiş oluştur
        history = []
        for role, content in messages:
            gemini_role = "user" if role == "user" else "model"
            history.append({"role": gemini_role, "parts": [{"text": content}]})
        
        return history
    except Exception as e:
        print(f"Konuşma geçmişi alınırken hata: {str(e)}")
        return []  # Hata durumunda boş liste döndür

def save_session_score(user_id, session_id, character, session_ratings):
    """Oturum puan ortalamasını kaydet"""
    if session_id not in session_ratings:
        print("Puanlar bulunamadı.")
        return

    scores = session_ratings[session_id]
    avg_score = sum(scores) / len(scores)

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO session_scores (user_id, session_id, character, avg_score, timestamp) VALUES (?, ?, ?, ?, ?)",
            (user_id, session_id, character, avg_score, datetime.now().isoformat())
        )

        conn.commit()
        conn.close()
        print(f"Ortalama puan {avg_score} kaydedildi.")
    except Exception as e:
        print(f"Veritabanı hatası: {str(e)}")
