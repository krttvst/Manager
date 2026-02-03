from sqlalchemy.orm import Session

from app.models.channel import Channel
from app.models.post import Post
from app.models.source_item import SourceItem


def list_channels(db: Session) -> list[Channel]:
    return db.query(Channel).all()


def get_channel(db: Session, channel_id: int) -> Channel | None:
    return db.get(Channel, channel_id)


def get_channel_by_identifier(db: Session, identifier: str) -> Channel | None:
    return db.query(Channel).filter(Channel.telegram_channel_identifier == identifier).first()


def create_channel(db: Session, channel: Channel) -> Channel:
    db.add(channel)
    db.commit()
    db.refresh(channel)
    return channel


def delete_channel(db: Session, channel: Channel) -> None:
    db.delete(channel)
    db.commit()


def get_post_ids_for_channel(db: Session, channel_id: int) -> list[int]:
    return [row[0] for row in db.query(Post.id).filter(Post.channel_id == channel_id).all()]


def delete_source_items_for_posts(db: Session, post_ids: list[int]) -> None:
    if not post_ids:
        return
    db.query(SourceItem).filter(SourceItem.post_id.in_(post_ids)).delete(synchronize_session=False)


def delete_posts_for_channel(db: Session, post_ids: list[int]) -> None:
    if not post_ids:
        return
    db.query(Post).filter(Post.id.in_(post_ids)).delete(synchronize_session=False)
