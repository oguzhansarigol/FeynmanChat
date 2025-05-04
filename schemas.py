from pydantic import BaseModel

# Tek seferlik soru üretimi için
class QuestionRequest(BaseModel):
    character: str
    topic: str

class QuestionResponse(BaseModel):
    questions: list[str]

# Sohbet başlatma ve devam ettirme için
class ChatRequest(BaseModel):
    user_id: int 
    session_id: str       # UUID olabilir, frontend'de üretilip gönderilir
    character: str
    message: str           # Kullanıcının yazdığı mesaj

class ChatResponse(BaseModel):
    reply: str             # AI tarafından dönen yanıt
