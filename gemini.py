import os
import json
from dotenv import load_dotenv
from datetime import datetime
import google.generativeai as genai

from database import save_message, get_conversation, save_session_score

session_ratings = {}  

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

def start_conversation(user_id: int, session_id: str, character: str, user_input: str) -> dict:
    """Kullanıcı ve karakter arasında sohbeti yürütür"""
    try:
        # Eğer konuşma "bitir" komutu ile sonlandırıldıysa, ortalama puan kaydedilecek
        if user_input.lower() == "dur":
            print(session_ratings)
            save_session_score(user_id, session_id, character,session_ratings)
            return {"reply": "Görüşme bitirildi. Puan ortalaması kaydedildi."}

        prompts = load_prompts()
        if character not in prompts:
            raise ValueError(f"Geçersiz karakter: {character}")
        
        # Konuşma geçmişini al (son 10 mesajı)
        history = get_conversation(user_id, session_id)
        
        # İlk mesaj, konuyu belirlemedir. Bunu kaydetme.
        if len(history) == 0:
            character_prompt = prompts[character].replace("{topic}", user_input)
        else:
            # Eğer geçmiş konuşmalar varsa, karakterin son mesajı ile devam et.
            character_prompt = prompts[character].replace("{topic}", history[-1]['parts'][0]['text'])

        # Gemini API ile konuşmayı başlat
        try:
            chat = model.start_chat(history=history if history else None)
            instruction = f"{character_prompt}\n\nKullanıcı mesajı: {user_input}\n\nBir soru ile yanıt ver."
            response = chat.send_message(instruction)
            ai_reply = response.text.strip()

            # Mesajları kaydet
            save_message(user_id, session_id, character, "user", user_input)
            save_message(user_id, session_id, character, "ai", ai_reply)

            # AI cevabına göre değerlendirme yap
            if len(history) > 0:  # İlk mesaj değilse
                score = evaluate_answer_with_gemini(ai_reply, user_input)
                if session_id not in session_ratings:
                    session_ratings[session_id] = []
                session_ratings[session_id].append(score)

            return {"reply": ai_reply}
        
        except Exception as e:
            print(f"Gemini API hatası: {str(e)}")
            return {"reply": "Üzgünüm, bir sorun oluştu. Lütfen tekrar deneyin."}
    
    except Exception as e:
        print(f"Genel hata: {str(e)}")
        raise Exception(f"Gemini API sohbet hatası: {str(e)}")
    
def evaluate_answer_with_gemini(ai_reply: str, user_input: str) -> int:
    """Gemini ile cevabı 1-5 arasında değerlendir"""
    prompt = f"Aşağıdaki soruyu değerlendir ve cevabın doğruluğunu 1 ile 5 arasında puanla:\n\nAI Sorusu: {ai_reply}\n\nKullanıcı Cevabı: {user_input}\n\nSadece sayı olarak dön:"

    try:
        response = model.generate_content(prompt)
        score_text = response.text.strip()
        score = int(score_text)
        return max(1, min(score, 5))  # 1-5 arasında sınırla
    except Exception as e:
        print(f"Değerlendirme hatası: {str(e)}")
        return 3  # Varsayılan değer
