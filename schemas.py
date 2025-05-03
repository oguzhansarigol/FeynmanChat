from pydantic import BaseModel

class QuestionRequest(BaseModel):
    character: str
    topic: str

class QuestionResponse(BaseModel):
    questions: list[str]
