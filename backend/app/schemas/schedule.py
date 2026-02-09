from datetime import datetime

from pydantic import BaseModel

from app.models.enums import PostStatus


class ScheduledPostItem(BaseModel):
    id: int
    channel_id: int
    channel_title: str | None = None
    title: str
    status: PostStatus
    scheduled_at: datetime | None = None
    updated_at: datetime
    last_error: str | None = None


class ScheduledPostListOut(BaseModel):
    items: list[ScheduledPostItem]
    total: int
    limit: int
    offset: int


class RequeueRequest(BaseModel):
    delay_seconds: int = 60

