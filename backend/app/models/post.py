from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.models.enums import PostStatus


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    channel_id: Mapped[int] = mapped_column(ForeignKey("channels.id"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    body_text: Mapped[str] = mapped_column(Text)
    media_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[PostStatus] = mapped_column(default=PostStatus.draft, index=True)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    telegram_message_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    last_known_views: Mapped[int | None] = mapped_column(nullable=True)
    publish_attempts: Mapped[int] = mapped_column(default=0)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    updated_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    editor_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    channel = relationship("Channel")
    author = relationship("User", foreign_keys=[created_by])
    editor = relationship("User", foreign_keys=[updated_by])
