from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from schemas import QuestionRequest, QuestionResponse, ChatRequest, ChatResponse
from gemini import generate_questions, start_conversation
from database import init_db

# Veritabanını başlat
init_db()

# FastAPI uygulaması
app = FastAPI(
    title="FeynmanChat - AI Mentor App",
    description="Karakter tabanlı soru üretimi ve sohbet deneyimi sunan yapay zekâ destekli öğrenme uygulaması.",
    version="2.0.0"
)

# Statik dosya ve template dizinleri
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# CORS (frontend erişimi için)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ana sayfa
@app.get("/", response_class=HTMLResponse)
def get_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Eski sistem: Konuya özel 3 soru üret
@app.post("/ask", response_model=QuestionResponse)
async def ask_questions(payload: QuestionRequest):
    try:
        result = generate_questions(payload.character, payload.topic)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Sunucu hatası: " + str(e))

# Yeni sistem: Karakterle sürekli konuşma
@app.post("/chat", response_model=ChatResponse)
async def chat_with_character(payload: ChatRequest):
    try:
        result = start_conversation(payload.session_id, payload.character, payload.message)
        return ChatResponse(**result)  # ✅ garanti dönüşüm
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Sunucu hatası: " + str(e))

