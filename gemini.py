import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from database import log_request

# .env dosyasından API key'i oku
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini API anahtarı ayarla
genai.configure(api_key=API_KEY)

# Modeli başlat (gemini-1.5-pro)
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
    prompt = create_prompt(character, topic)

    try:
        response = model.generate_content(prompt)
        text_block = response.text
        questions = [q.strip("- ").strip() for q in text_block.strip().split("\n") if q.strip()]
    except Exception as e:
        raise Exception(f"Gemini API hatası: {str(e)}")

    # Log kaydı
    log_request(character, topic, prompt, json.dumps(questions, ensure_ascii=False))


    return {"questions": questions}
