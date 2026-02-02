from datetime import datetime
from pydantic import BaseModel


class ChannelCreate(BaseModel):
    title: str
    telegram_channel_identifier: str


class ChannelOut(BaseModel):
    id: int
    title: str
    telegram_channel_identifier: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
