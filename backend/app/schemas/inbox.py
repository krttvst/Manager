from datetime import datetime

from pydantic import BaseModel


class SuggestionInboxItem(BaseModel):
    id: int
    channel_id: int
    channel_title: str | None = None
    title: str
    body_text: str
    media_url: str | None
    source_url: str | None
    source_hash: str
    created_at: datetime


class SuggestionInboxOut(BaseModel):
    items: list[SuggestionInboxItem]
    total: int
    limit: int
    offset: int

