from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.post import Post
from app.models.post_comment import PostComment
from app.models.user import User
from app.repositories import comments as comment_repo
from app.schemas.comments import PostCommentCreate, PostCommentOut


def list_post_comments(db: Session, post_id: int, limit: int = 100, offset: int = 0) -> list[PostCommentOut]:
    post = db.get(Post, int(post_id))
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    comments = comment_repo.list_comments_for_post(db, post_id, limit=limit, offset=offset)
    if not comments:
        return []

    author_ids = {c.author_user_id for c in comments}
    authors = db.execute(select(User.id, User.email).where(User.id.in_(author_ids))).all()
    email_by_id = {int(r[0]): r[1] for r in authors}

    return [
        PostCommentOut(
            id=c.id,
            post_id=c.post_id,
            author_user_id=c.author_user_id,
            author_email=email_by_id.get(int(c.author_user_id)),
            kind=c.kind,
            body_text=c.body_text,
            created_at=c.created_at,
        )
        for c in comments
    ]


def create_post_comment(db: Session, post_id: int, payload: PostCommentCreate, user) -> PostCommentOut:
    post = db.get(Post, int(post_id))
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    body = (payload.body_text or "").strip()
    if not body:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Comment is empty")

    comment = PostComment(post_id=int(post_id), author_user_id=int(user.id), kind="comment", body_text=body)
    created = comment_repo.create_comment(db, comment)
    author = db.get(User, int(user.id))
    return PostCommentOut(
        id=created.id,
        post_id=created.post_id,
        author_user_id=created.author_user_id,
        author_email=author.email if author else None,
        kind=created.kind,
        body_text=created.body_text,
        created_at=created.created_at,
    )

