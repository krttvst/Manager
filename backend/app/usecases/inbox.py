from __future__ import annotations

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.channel import Channel
from app.models.suggestion import Suggestion
from app.schemas.inbox import SuggestionInboxItem, SuggestionInboxOut

MAX_LIMIT = 200


def list_suggestions_inbox(
    db: Session,
    *,
    limit: int = 50,
    offset: int = 0,
    channel_id: int | None = None,
    q: str | None = None,
) -> SuggestionInboxOut:
    safe_limit = max(1, min(int(limit), MAX_LIMIT))
    safe_offset = max(0, int(offset))

    base = (
        select(
            Suggestion.id,
            Suggestion.channel_id,
            Channel.title.label("channel_title"),
            Suggestion.title,
            Suggestion.body_text,
            Suggestion.media_url,
            Suggestion.source_url,
            Suggestion.source_hash,
            Suggestion.created_at,
        )
        .select_from(Suggestion)
        .join(Channel, Channel.id == Suggestion.channel_id, isouter=True)
    )
    count_stmt = select(func.count()).select_from(Suggestion)

    if channel_id is not None:
        base = base.where(Suggestion.channel_id == int(channel_id))
        count_stmt = count_stmt.where(Suggestion.channel_id == int(channel_id))

    if q:
        like = f"%{q.strip()}%"
        filt = or_(
            Suggestion.title.ilike(like),
            Suggestion.body_text.ilike(like),
            Suggestion.source_url.ilike(like),
        )
        base = base.where(filt)
        count_stmt = count_stmt.where(filt)

    total = int(db.execute(count_stmt).scalar_one())
    rows = db.execute(base.order_by(Suggestion.created_at.desc()).limit(safe_limit).offset(safe_offset)).all()

    items = [
        SuggestionInboxItem(
            id=int(r.id),
            channel_id=int(r.channel_id),
            channel_title=getattr(r, "channel_title", None),
            title=r.title,
            body_text=r.body_text,
            media_url=r.media_url,
            source_url=r.source_url,
            source_hash=r.source_hash,
            created_at=r.created_at,
        )
        for r in rows
    ]
    return SuggestionInboxOut(items=items, total=total, limit=safe_limit, offset=safe_offset)

