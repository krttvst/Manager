from datetime import datetime
from pydantic import BaseModel
from app.models.enums import PostStatus


class PostCreate(BaseModel):
    title: str
    body_text: str
    media_url: str | None = None


class PostUpdate(BaseModel):
    title: str | None = None
    body_text: str | None = None
    media_url: str | None = None


class PostOut(BaseModel):
    id: int
    channel_id: int
    title: str
    body_text: str
    media_url: str | None
    status: PostStatus
    scheduled_at: datetime | None
    published_at: datetime | None
    telegram_message_id: str | None
    last_known_views: int | None
    publish_attempts: int
    last_error: str | None
    editor_comment: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ScheduleRequest(BaseModel):
    scheduled_at: datetime


class RejectRequest(BaseModel):
    comment: str
