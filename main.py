from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from schemas import QuestionRequest, QuestionResponse
from gemini import generate_questions
from database import init_db

# Veritabanını başlat
init_db()

# FastAPI app
app = FastAPI(
    title="FeynmanChat - AI Mentor App",
    description="Karakter tabanlı soru üretimi yapan yapay zekâ destekli öğrenme uygulaması.",
    version="1.0.0"
)

# Statik ve template dizinlerini bağla
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# CORS ayarı
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ana sayfa (HTML UI)
@app.get("/", response_class=HTMLResponse)
def get_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# API endpoint
@app.post("/ask", response_model=QuestionResponse)
async def ask_questions(payload: QuestionRequest):
    try:
        result = generate_questions(payload.character, payload.topic)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Sunucu hatası: " + str(e))
