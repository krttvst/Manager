from sqlalchemy.orm import Session

from app.schemas.channel import ChannelCreate
from app.models.channel import Channel
from app.usecases import channels as channel_usecase


# Backwards-compatible service wrappers delegating to use-cases.

def list_channels(db: Session) -> list[Channel]:
    return channel_usecase.list_channels(db)


def get_channel(db: Session, channel_id: int) -> Channel:
    return channel_usecase.get_channel(db, channel_id)


def create_channel(db: Session, payload: ChannelCreate) -> Channel:
    return channel_usecase.create_channel(db, payload)


def delete_channel(db: Session, channel_id: int, user) -> None:
    return channel_usecase.delete_channel(db, channel_id, user)
