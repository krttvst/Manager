from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.api.deps import get_current_user, require_roles
from app.models.enums import PostStatus, UserRole
from app.schemas.post import PostCreate, PostOut, PostUpdate, ScheduleRequest, RejectRequest, PostListOut
from app.usecases import posts as post_usecase

router = APIRouter(prefix="", tags=["posts"])


@router.post("/channels/{channel_id}/posts", response_model=PostOut)
def create_post(
    channel_id: int,
    payload: PostCreate,
    db: Session = Depends(get_db),
    user=Depends(require_roles(UserRole.author, UserRole.editor, UserRole.admin)),
):
    return post_usecase.create_post(db, channel_id, payload, user)


@router.get("/channels/{channel_id}/posts", response_model=list[PostListOut])
def list_posts(
    channel_id: int,
    status_filter: PostStatus | None = None,
    status_filters: list[PostStatus] | None = Query(None),
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    filters = status_filters or ([status_filter] if status_filter else None)
    return post_usecase.list_posts(db, channel_id, filters, limit=limit, offset=offset)


@router.get("/posts/{post_id}", response_model=PostOut)
def get_post(
    post_id: int,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    return post_usecase.get_post(db, post_id)


@router.put("/posts/{post_id}", response_model=PostOut)
def update_post(
    post_id: int,
    payload: PostUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_roles(UserRole.author, UserRole.editor, UserRole.admin)),
):
    return post_usecase.update_post(db, post_id, payload, user)


@router.post("/posts/{post_id}/submit-approval", response_model=PostOut)
def submit_approval(
    post_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles(UserRole.author, UserRole.editor, UserRole.admin)),
):
    return post_usecase.submit_approval(db, post_id, user)


@router.post("/posts/{post_id}/approve", response_model=PostOut)
def approve_post(
    post_id: int,
    db: Session = Depends(get_db),
    _editor=Depends(require_roles(UserRole.editor, UserRole.admin)),
    user=Depends(get_current_user),
):
    return post_usecase.approve_post(db, post_id, user)


@router.post("/posts/{post_id}/reject", response_model=PostOut)
def reject_post(
    post_id: int,
    payload: RejectRequest,
    db: Session = Depends(get_db),
    _editor=Depends(require_roles(UserRole.editor, UserRole.admin)),
    user=Depends(get_current_user),
):
    return post_usecase.reject_post(db, post_id, payload, user)


@router.post("/posts/{post_id}/schedule", response_model=PostOut)
def schedule_post(
    post_id: int,
    payload: ScheduleRequest,
    db: Session = Depends(get_db),
    _editor=Depends(require_roles(UserRole.editor, UserRole.admin)),
    user=Depends(get_current_user),
):
    return post_usecase.schedule_post(db, post_id, payload, user)


@router.post("/posts/{post_id}/publish-now", response_model=PostOut)
def publish_now(
    post_id: int,
    db: Session = Depends(get_db),
    _editor=Depends(require_roles(UserRole.editor, UserRole.admin)),
    user=Depends(get_current_user),
):
    return post_usecase.publish_now(db, post_id, user)


@router.delete("/posts/{post_id}", status_code=204)
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
    _admin=Depends(require_roles(UserRole.admin)),
):
    post_usecase.delete_post(db, post_id, user)
