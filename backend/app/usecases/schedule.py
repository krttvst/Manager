from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.channel import Channel
from app.models.enums import PostStatus
from app.models.post import Post
from app.schemas.schedule import ScheduledPostItem, ScheduledPostListOut
from app.services.audit import log_action

MAX_LIMIT = 200


def list_scheduled_posts(
    db: Session,
    *,
    limit: int = 50,
    offset: int = 0,
    channel_id: int | None = None,
    since: datetime | None = None,
    until: datetime | None = None,
) -> ScheduledPostListOut:
    safe_limit = max(1, min(int(limit), MAX_LIMIT))
    safe_offset = max(0, int(offset))

    base = (
        select(
            Post.id,
            Post.channel_id,
            Channel.title.label("channel_title"),
            Post.title,
            Post.status,
            Post.scheduled_at,
            Post.updated_at,
            Post.last_error,
        )
        .select_from(Post)
        .join(Channel, Channel.id == Post.channel_id, isouter=True)
        .where(Post.status == PostStatus.scheduled)
    )
    count_stmt = select(func.count()).select_from(Post).where(Post.status == PostStatus.scheduled)

    if channel_id is not None:
        base = base.where(Post.channel_id == int(channel_id))
        count_stmt = count_stmt.where(Post.channel_id == int(channel_id))
    if since is not None:
        base = base.where(Post.scheduled_at.is_not(None)).where(Post.scheduled_at >= since)
        count_stmt = count_stmt.where(Post.scheduled_at.is_not(None)).where(Post.scheduled_at >= since)
    if until is not None:
        base = base.where(Post.scheduled_at.is_not(None)).where(Post.scheduled_at <= until)
        count_stmt = count_stmt.where(Post.scheduled_at.is_not(None)).where(Post.scheduled_at <= until)

    total = int(db.execute(count_stmt).scalar_one())
    rows = db.execute(base.order_by(Post.scheduled_at.asc().nullslast()).limit(safe_limit).offset(safe_offset)).all()
    items = [
        ScheduledPostItem(
            id=int(r.id),
            channel_id=int(r.channel_id),
            channel_title=getattr(r, "channel_title", None),
            title=r.title,
            status=r.status,
            scheduled_at=r.scheduled_at,
            updated_at=r.updated_at,
            last_error=r.last_error,
        )
        for r in rows
    ]
    return ScheduledPostListOut(items=items, total=total, limit=safe_limit, offset=safe_offset)


def requeue_failed_post(db: Session, *, post_id: int, actor_user_id: int, delay_seconds: int = 60) -> Post:
    post = db.get(Post, int(post_id))
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if post.status not in {PostStatus.failed, PostStatus.scheduled}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Post is not requeueable")
    delay = max(0, int(delay_seconds))
    now = datetime.utcnow()
    post.status = PostStatus.scheduled
    post.scheduled_at = now + timedelta(seconds=delay)
    post.updated_by = actor_user_id
    post.updated_at = now
    log_action(db, "post", post.id, "requeue", actor_user_id, {"delay_seconds": delay})
    db.commit()
    return post
