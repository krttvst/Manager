from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.post import Post
from app.models.source_item import SourceItem

EXCERPT_CHARS = 200
MAX_LIST_LIMIT = 200
DEFAULT_LIST_LIMIT = 50


def get_post(db: Session, post_id: int) -> Post | None:
    return db.get(Post, post_id)


def list_posts_compact(
    db: Session,
    channel_id: int,
    status_filters,
    limit: int = DEFAULT_LIST_LIMIT,
    offset: int = 0,
) -> list[dict]:
    safe_limit = max(1, min(limit, MAX_LIST_LIMIT))
    safe_offset = max(0, offset)
    stmt = select(
        Post.id,
        Post.channel_id,
        Post.title,
        func.substr(func.coalesce(Post.body_text, ""), 1, EXCERPT_CHARS).label("body_excerpt"),
        Post.media_url,
        Post.status,
        Post.scheduled_at,
        Post.published_at,
        Post.telegram_message_id,
        Post.last_known_views,
        Post.last_error,
        Post.editor_comment,
        Post.created_at,
        Post.updated_at,
    ).where(Post.channel_id == channel_id)
    if status_filters:
        stmt = stmt.where(Post.status.in_(status_filters))
    stmt = stmt.order_by(Post.created_at.desc()).limit(safe_limit).offset(safe_offset)
    rows = db.execute(stmt).all()
    return [dict(row._mapping) for row in rows]


def update_last_known_views(db: Session, post_id: int, views: int) -> None:
    db.query(Post).filter(Post.id == post_id).update({Post.last_known_views: views}, synchronize_session=False)
    db.commit()


def create_post(db: Session, post: Post) -> Post:
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


def save_post(db: Session, post: Post) -> Post:
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


def delete_post(db: Session, post: Post) -> None:
    db.delete(post)
    db.commit()


def delete_source_items_for_post(db: Session, post_id: int) -> None:
    db.query(SourceItem).filter(SourceItem.post_id == post_id).delete(synchronize_session=False)
