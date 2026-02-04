from datetime import datetime
from pydantic import BaseModel


class SuggestionCreate(BaseModel):
    title: str
    body_text: str
    media_url: str | None = None
    source_url: str | None = None


class SuggestionOut(BaseModel):
    id: int
    channel_id: int
    title: str
    body_text: str
    media_url: str | None
    source_url: str | None
    source_hash: str
    created_at: datetime

    class Config:
        from_attributes = True
