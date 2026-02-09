from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class PostComment(Base):
    __tablename__ = "post_comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), index=True)
    author_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    # comment: user-provided; reject: editor rejection reason; system: internal notes if needed later
    kind: Mapped[str] = mapped_column(String(16), default="comment")
    body_text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    post = relationship("Post")
    author = relationship("User")

