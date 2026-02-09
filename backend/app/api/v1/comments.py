from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.deps import get_db
from app.schemas.comments import PostCommentCreate, PostCommentOut
from app.usecases import comments as comments_usecase

router = APIRouter(prefix="/posts/{post_id}/comments", tags=["comments"])


@router.get("", response_model=list[PostCommentOut])
def list_comments(
    post_id: int,
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    return comments_usecase.list_post_comments(db, post_id, limit=limit, offset=offset)


@router.post("", response_model=PostCommentOut)
def create_comment(
    post_id: int,
    payload: PostCommentCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return comments_usecase.create_post_comment(db, post_id, payload, user)

