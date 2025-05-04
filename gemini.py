import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

from database import save_message, get_conversation

# .env dosyasından API key'i oku
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini API yapılandırması
genai.configure(api_key=API_KEY)

# Model başlat
model = genai.GenerativeModel("gemini-1.5-pro")

def load_prompts(path="prompts.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def create_prompt(character: str, topic: str) -> str:
    templates = load_prompts()
    if character not in templates:
        raise ValueError("Geçersiz karakter seçimi")
    return templates[character].replace("{topic}", topic)

def generate_questions(character: str, topic: str) -> dict:
    """Tek seferlik 3 soru üretir (eski sistem)"""
    prompt = create_prompt(character, topic)

    try:
        response = model.generate_content(prompt)
        text_block = response.text
        questions = [q.strip("- ").strip() for q in text_block.strip().split("\n") if q.strip()]
    except Exception as e:
        raise Exception(f"Gemini API hatası: {str(e)}")

    return {"questions": questions[:3]}  # En fazla 3 soru döndür

def start_conversation(session_id: str, character: str, user_input: str) -> dict:
    """Kullanıcı ve seçilen karakter arasında sohbet başlatır veya devam ettirir"""
    try:
        # Karakter talimatlarını getir
        prompts = load_prompts()
        if character not in prompts:
            raise ValueError(f"Geçersiz karakter: {character}")
        
        # Konuşma geçmişini getir
        history = get_conversation(session_id)
        
        # Konuşma geçmişi kontrolü
        # Son 5 mesajı al (token limitlerini aşmamak için)
        if len(history) > 10:
            history = history[-10:]
        
        # İlk mesaj ise, karakter tanımını ekle
        character_prompt = prompts[character].replace("{topic}", "")
        
        # Gemini API için mesaj oluştur
        try:
            # Yeni bir sohbet başlat
            chat = model.start_chat(history=history if history else None)
            
            # Kullanıcı mesajı ve karakter talimatını birleştir
            instruction = f"{character_prompt}\n\nKullanıcı mesajı: {user_input}\n\nBir soru ile yanıt ver."
            response = chat.send_message(instruction)
            
            ai_reply = response.text.strip()
            
            # DB'ye gerçek kullanıcı girdisi ve AI cevabını kaydet
            save_message(session_id, character, "user", user_input)
            save_message(session_id, character, "ai", ai_reply)
            
            return {"reply": ai_reply}
        
        except Exception as e:
            print(f"Gemini API hatası: {str(e)}")
            # Basit bir yanıt döndür
            return {"reply": "Üzgünüm, bir sorun oluştu. Lütfen tekrar deneyin."}
    
    except Exception as e:
        print(f"Genel hata: {str(e)}")
        raise Exception(f"Gemini API sohbet hatası: {str(e)}")