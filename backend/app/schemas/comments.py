from datetime import datetime

from pydantic import BaseModel


class PostCommentCreate(BaseModel):
    body_text: str


class PostCommentOut(BaseModel):
    id: int
    post_id: int
    author_user_id: int
    author_email: str | None = None
    kind: str
    body_text: str
    created_at: datetime

    class Config:
        from_attributes = True

