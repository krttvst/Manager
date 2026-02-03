from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.channel import Channel
from app.repositories import channels as channel_repo
from app.schemas.channel import ChannelCreate, ChannelLookupResponse
from app.services.audit import log_action
from app.services import telegram as telegram_service


def list_channels(db: Session) -> list[Channel]:
    return channel_repo.list_channels(db)


def get_channel(db: Session, channel_id: int) -> Channel:
    channel = channel_repo.get_channel(db, channel_id)
    if not channel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")
    return channel


def create_channel(db: Session, payload: ChannelCreate) -> Channel:
    existing = channel_repo.get_channel_by_identifier(db, payload.telegram_channel_identifier)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Channel already exists")
    channel = Channel(
        title=payload.title,
        telegram_channel_identifier=payload.telegram_channel_identifier,
        avatar_url=payload.avatar_url,
    )
    return channel_repo.create_channel(db, channel)


def delete_channel(db: Session, channel_id: int, user) -> None:
    channel = channel_repo.get_channel(db, channel_id)
    if not channel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")

    post_ids = channel_repo.get_post_ids_for_channel(db, channel_id)
    channel_repo.delete_source_items_for_posts(db, post_ids)
    channel_repo.delete_posts_for_channel(db, post_ids)
    channel_repo.delete_channel(db, channel)
    log_action(db, "channel", channel_id, "delete", user.id, {"post_ids": post_ids})


def lookup_channel(db: Session, identifier: str) -> ChannelLookupResponse:
    try:
        lookup = telegram_service.lookup_channel_profile(identifier)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return ChannelLookupResponse(title=lookup["title"], avatar_url=lookup.get("avatar_url"))


def auto_add_channel_from_telegram(db: Session, chat_id: str, username: str | None, title: str | None) -> Channel:
    identifier = f"@{username}" if username else str(chat_id)
    existing = channel_repo.get_channel_by_identifier(db, identifier)
    if existing:
        return existing
    lookup = telegram_service.lookup_channel_profile(identifier)
    channel = Channel(
        title=lookup.get("title") or title or identifier,
        telegram_channel_identifier=identifier,
        avatar_url=lookup.get("avatar_url"),
    )
    return channel_repo.create_channel(db, channel)
