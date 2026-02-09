from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.post_comment import PostComment


def create_comment(db: Session, comment: PostComment) -> PostComment:
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def list_comments_for_post(db: Session, post_id: int, limit: int = 100, offset: int = 0) -> list[PostComment]:
    safe_limit = max(1, min(int(limit), 200))
    safe_offset = max(0, int(offset))
    stmt = (
        select(PostComment)
        .where(PostComment.post_id == int(post_id))
        .order_by(PostComment.created_at.asc())
        .limit(safe_limit)
        .offset(safe_offset)
    )
    rows = db.execute(stmt).scalars().all()
    return list(rows)

