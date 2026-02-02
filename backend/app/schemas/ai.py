from pydantic import BaseModel


class AiGenerateRequest(BaseModel):
    url: str
    tone: str = "neutral"
    length: str = "medium"
    language: str = "ru"


class AiGenerateResponse(BaseModel):
    title: str
    body_text: str
    source_url: str
