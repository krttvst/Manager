from datetime import datetime
from pydantic import BaseModel


class ChannelCreate(BaseModel):
    title: str
    telegram_channel_identifier: str
    avatar_url: str | None = None


class ChannelOut(BaseModel):
    id: int
    title: str
    telegram_channel_identifier: str
    is_active: bool
    avatar_url: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class ChannelLookupResponse(BaseModel):
    title: str
    avatar_url: str | None = None
