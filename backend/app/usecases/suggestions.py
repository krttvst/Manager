from fastapi import HTTPException, status
import hashlib
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.channel import Channel
from app.models.post import Post
from app.models.suggestion import Suggestion
from app.repositories import suggestions as suggestion_repo
from app.repositories import posts as post_repo
from app.schemas.suggestion import SuggestionCreate
from app.services.audit import log_action
from app.metrics import SUGGESTION_CREATED_TOTAL


def create_suggestion(db: Session, channel_id: int, payload: SuggestionCreate) -> Suggestion:
    channel = db.get(Channel, channel_id)
    if not channel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")
    source_basis = payload.source_url or f"{payload.title}\n{payload.body_text}"
    source_hash = hashlib.sha256(source_basis.encode("utf-8")).hexdigest()
    suggestion = Suggestion(
        channel_id=channel_id,
        title=payload.title,
        body_text=payload.body_text,
        media_url=payload.media_url,
        source_url=payload.source_url,
        source_hash=source_hash,
    )
    try:
        created = suggestion_repo.create_suggestion(db, suggestion)
        SUGGESTION_CREATED_TOTAL.inc()
        return created
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Suggestion already exists")


def list_suggestions(db: Session, channel_id: int, limit: int, offset: int) -> list[Suggestion]:
    channel = db.get(Channel, channel_id)
    if not channel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")
    return suggestion_repo.list_suggestions(db, channel_id, limit=limit, offset=offset)


def accept_suggestion(db: Session, channel_id: int, suggestion_id: int, user) -> Post:
    suggestion = suggestion_repo.get_suggestion(db, suggestion_id)
    if not suggestion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Suggestion not found")
    if suggestion.channel_id != channel_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Suggestion not found")
    post = Post(
        channel_id=suggestion.channel_id,
        title=suggestion.title,
        body_text=suggestion.body_text,
        media_url=suggestion.media_url,
        created_by=user.id,
        updated_by=user.id,
    )
    post = post_repo.create_post(db, post)
    suggestion_repo.delete_suggestion(db, suggestion)
    log_action(db, "suggestion", suggestion_id, "accept", user.id, {"post_id": post.id})
    return post


def reject_suggestion(db: Session, channel_id: int, suggestion_id: int, user) -> None:
    suggestion = suggestion_repo.get_suggestion(db, suggestion_id)
    if not suggestion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Suggestion not found")
    if suggestion.channel_id != channel_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Suggestion not found")
    suggestion_repo.delete_suggestion(db, suggestion)
    log_action(db, "suggestion", suggestion_id, "reject", user.id, {})
