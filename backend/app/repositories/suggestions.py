from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.suggestion import Suggestion

MAX_LIST_LIMIT = 200
DEFAULT_LIST_LIMIT = 50


def create_suggestion(db: Session, suggestion: Suggestion) -> Suggestion:
    db.add(suggestion)
    db.commit()
    db.refresh(suggestion)
    return suggestion


def list_suggestions(
    db: Session,
    channel_id: int,
    limit: int = DEFAULT_LIST_LIMIT,
    offset: int = 0,
) -> list[Suggestion]:
    safe_limit = max(1, min(limit, MAX_LIST_LIMIT))
    safe_offset = max(0, offset)
    stmt = (
        select(Suggestion)
        .where(Suggestion.channel_id == channel_id)
        .order_by(Suggestion.created_at.desc())
        .limit(safe_limit)
        .offset(safe_offset)
    )
    return list(db.execute(stmt).scalars().all())


def get_suggestion(db: Session, suggestion_id: int) -> Suggestion | None:
    return db.get(Suggestion, suggestion_id)


def delete_suggestion(db: Session, suggestion: Suggestion) -> None:
    db.delete(suggestion)
    db.commit()
