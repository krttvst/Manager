from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, Float, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class AgentSettings(Base):
    __tablename__ = "agent_settings"

    id: Mapped[int] = mapped_column(primary_key=True)
    channel_id: Mapped[int] = mapped_column(ForeignKey("channels.id"), unique=True, index=True)
    length: Mapped[int] = mapped_column(Integer, default=400)
    style: Mapped[str] = mapped_column(String(64), default="формальный")
    format: Mapped[str] = mapped_column(String(64), default="статья")
    temperature: Mapped[float] = mapped_column(Float, default=0.4)
    extra: Mapped[str | None] = mapped_column(Text, nullable=True)
    tone_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    tone_values: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    channel = relationship("Channel")
