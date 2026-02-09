from datetime import datetime

from pydantic import BaseModel

from app.models.enums import PostStatus


class DashboardChannelSummary(BaseModel):
    channel_id: int
    next_scheduled_at: datetime | None = None
    overdue_scheduled_count: int = 0
    last_post_at: datetime | None = None
    last_published_at: datetime | None = None
    status_counts: dict[PostStatus, int] = {}


class DashboardUpcomingPost(BaseModel):
    post_id: int
    channel_id: int
    channel_title: str | None = None
    title: str
    scheduled_at: datetime


class DashboardRecentError(BaseModel):
    post_id: int
    channel_id: int
    channel_title: str | None = None
    title: str
    last_error: str
    updated_at: datetime


class DashboardOverview(BaseModel):
    now: datetime
    total_status_counts: dict[PostStatus, int] = {}
    channels: list[DashboardChannelSummary] = []
    upcoming: list[DashboardUpcomingPost] = []
    recent_errors: list[DashboardRecentError] = []

