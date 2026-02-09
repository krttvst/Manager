from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.channel import Channel
from app.models.enums import PostStatus
from app.models.post import Post
from app.schemas.dashboard import (
    DashboardChannelSummary,
    DashboardOverview,
    DashboardRecentError,
    DashboardUpcomingPost,
)


def get_overview(db: Session, *, now: datetime | None = None, upcoming_limit: int = 20, errors_limit: int = 10) -> DashboardOverview:
    now = now or datetime.utcnow()

    # Status counts per channel and total.
    counts_rows = db.execute(
        select(Post.channel_id, Post.status, func.count().label("cnt")).group_by(Post.channel_id, Post.status)
    ).all()

    per_channel_counts: dict[int, dict[PostStatus, int]] = {}
    total_counts: dict[PostStatus, int] = {}
    for channel_id, status, cnt in counts_rows:
        per_channel_counts.setdefault(int(channel_id), {})[status] = int(cnt)
        total_counts[status] = int(total_counts.get(status, 0) + int(cnt))

    # Next scheduled in the future per channel.
    next_rows = db.execute(
        select(Post.channel_id, func.min(Post.scheduled_at).label("next_at"))
        .where(Post.status == PostStatus.scheduled)
        .where(Post.scheduled_at.is_not(None))
        .where(Post.scheduled_at > now)
        .group_by(Post.channel_id)
    ).all()
    next_by_channel = {int(r[0]): r[1] for r in next_rows}

    # Overdue scheduled count per channel.
    overdue_rows = db.execute(
        select(Post.channel_id, func.count().label("cnt"))
        .where(Post.status == PostStatus.scheduled)
        .where(Post.scheduled_at.is_not(None))
        .where(Post.scheduled_at <= now)
        .group_by(Post.channel_id)
    ).all()
    overdue_by_channel = {int(r[0]): int(r[1]) for r in overdue_rows}

    # Last post time per channel (any status).
    last_rows = db.execute(
        select(Post.channel_id, func.max(Post.created_at).label("last_post_at")).group_by(Post.channel_id)
    ).all()
    last_by_channel = {int(r[0]): r[1] for r in last_rows}

    # Last published time per channel.
    last_pub_rows = db.execute(
        select(Post.channel_id, func.max(Post.published_at).label("last_published_at"))
        .where(Post.published_at.is_not(None))
        .group_by(Post.channel_id)
    ).all()
    last_published_by_channel = {int(r[0]): r[1] for r in last_pub_rows}

    # Build channel summaries using channel list as ground truth so channels with zero posts still appear.
    channels = db.query(Channel).order_by(Channel.created_at.desc()).all()
    channel_summaries: list[DashboardChannelSummary] = []
    for ch in channels:
        channel_summaries.append(
            DashboardChannelSummary(
                channel_id=int(ch.id),
                next_scheduled_at=next_by_channel.get(int(ch.id)),
                overdue_scheduled_count=int(overdue_by_channel.get(int(ch.id), 0)),
                last_post_at=last_by_channel.get(int(ch.id)),
                last_published_at=last_published_by_channel.get(int(ch.id)),
                status_counts=per_channel_counts.get(int(ch.id), {}),
            )
        )

    # Global upcoming scheduled posts.
    upcoming_rows = db.execute(
        select(Post.id, Post.channel_id, Channel.title, Post.title, Post.scheduled_at)
        .join(Channel, Channel.id == Post.channel_id)
        .where(Post.status == PostStatus.scheduled)
        .where(Post.scheduled_at.is_not(None))
        .where(Post.scheduled_at > now)
        .order_by(Post.scheduled_at.asc())
        .limit(int(max(1, upcoming_limit)))
    ).all()
    upcoming = [
        DashboardUpcomingPost(
            post_id=int(r[0]),
            channel_id=int(r[1]),
            channel_title=r[2],
            title=r[3],
            scheduled_at=r[4],
        )
        for r in upcoming_rows
        if r[4] is not None
    ]

    # Global recent publish/edit errors.
    error_rows = db.execute(
        select(Post.id, Post.channel_id, Channel.title, Post.title, Post.last_error, Post.updated_at)
        .join(Channel, Channel.id == Post.channel_id)
        .where(Post.last_error.is_not(None))
        .order_by(Post.updated_at.desc())
        .limit(int(max(1, errors_limit)))
    ).all()
    recent_errors = [
        DashboardRecentError(
            post_id=int(r[0]),
            channel_id=int(r[1]),
            channel_title=r[2],
            title=r[3],
            last_error=r[4],
            updated_at=r[5],
        )
        for r in error_rows
        if r[4] is not None
    ]

    return DashboardOverview(
        now=now,
        total_status_counts=total_counts,
        channels=channel_summaries,
        upcoming=upcoming,
        recent_errors=recent_errors,
    )

