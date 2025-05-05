from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Depends
from pydantic import BaseModel
from database import create_user, get_user
from fastapi import Query
from database import get_all_conversations 
from database import get_full_conversation
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
@app.get("/chat", response_class=HTMLResponse)
def chat_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

"""
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
"""

# Yeni sistem: Karakterle sürekli konuşma
@app.post("/chat", response_model=ChatResponse)
async def chat_with_character(payload: ChatRequest):
    try:
        result = start_conversation(
    payload.user_id,
    payload.session_id,
    payload.character,
    payload.message
        )

        return ChatResponse(**result)  # bu kısım uygulama için önemli uğraştırdı baya, en doğru yaklaşım bu gibi
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Sunucu hatası: " + str(e))

#burası schemas.py dosyasına taşınacak
class RegisterRequest(BaseModel):
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/register")
def register_user(payload: RegisterRequest):
    try:
        create_user(payload.username, payload.password)
        return {"message": "Kayıt başarılı"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/login")
def login_user(payload: LoginRequest):
    user_id = get_user(payload.username, payload.password)
    if user_id:
        return {"user_id": user_id}
    else:
        raise HTTPException(status_code=401, detail="Kullanıcı adı veya şifre hatalı")

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/", response_class=HTMLResponse)
def home_redirect(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/chat-history/{user_id}")
def chat_history(user_id: int):
    try:
        history = get_all_conversations(user_id)
        return {"sessions": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.get("/chat-messages/{user_id}/{session_id}")
def get_session_messages(user_id: int, session_id: str):
    try:
        messages = get_full_conversation(user_id, session_id)
        return {"messages": messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))