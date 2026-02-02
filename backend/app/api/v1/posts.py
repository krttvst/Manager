from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.api.deps import get_current_user, require_roles
from app.models.post import Post
from app.models.enums import PostStatus, UserRole
from app.models.channel import Channel
from app.schemas.post import PostCreate, PostOut, PostUpdate, ScheduleRequest, RejectRequest
from app.services.audit import log_action
from app.services.telegram import publish_message
from app.core.config import settings

router = APIRouter(prefix="", tags=["posts"])


@router.post("/channels/{channel_id}/posts", response_model=PostOut)
def create_post(
    channel_id: int,
    payload: PostCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    channel = db.get(Channel, channel_id)
    if not channel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")
    post = Post(
        channel_id=channel_id,
        title=payload.title,
        body_text=payload.body_text,
        media_url=payload.media_url,
        created_by=user.id,
        updated_by=user.id,
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    log_action(db, "post", post.id, "create", user.id, {"status": post.status})
    return post


@router.get("/channels/{channel_id}/posts", response_model=list[PostOut])
def list_posts(
    channel_id: int,
    status_filter: PostStatus | None = None,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    query = db.query(Post).filter(Post.channel_id == channel_id)
    if status_filter:
        query = query.filter(Post.status == status_filter)
    return query.order_by(Post.created_at.desc()).all()


@router.put("/{post_id}", response_model=PostOut)
def update_post(
    post_id: int,
    payload: PostUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if post.status not in {PostStatus.draft, PostStatus.rejected}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Post is locked for editing")
    if user.role not in {UserRole.admin, UserRole.editor} and post.created_by != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to edit this post")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(post, field, value)
    post.updated_by = user.id
    post.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(post)
    log_action(db, "post", post.id, "update", user.id, {"status": post.status})
    return post


@router.post("/{post_id}/submit-approval", response_model=PostOut)
def submit_approval(
    post_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if post.status not in {PostStatus.draft, PostStatus.rejected}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status")
    if user.role not in {UserRole.admin, UserRole.editor} and post.created_by != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to submit this post")

    post.status = PostStatus.pending
    post.updated_by = user.id
    post.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(post)
    log_action(db, "post", post.id, "submit", user.id, {"status": post.status})
    return post


@router.post("/{post_id}/approve", response_model=PostOut)
def approve_post(
    post_id: int,
    db: Session = Depends(get_db),
    _editor=Depends(require_roles(UserRole.editor, UserRole.admin)),
    user=Depends(get_current_user),
):
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if post.status != PostStatus.pending:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status")

    post.status = PostStatus.approved
    post.editor_comment = None
    post.updated_by = user.id
    post.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(post)
    log_action(db, "post", post.id, "approve", user.id, {"status": post.status})
    return post


@router.post("/{post_id}/reject", response_model=PostOut)
def reject_post(
    post_id: int,
    payload: RejectRequest,
    db: Session = Depends(get_db),
    _editor=Depends(require_roles(UserRole.editor, UserRole.admin)),
    user=Depends(get_current_user),
):
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if post.status != PostStatus.pending:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status")

    post.status = PostStatus.rejected
    post.editor_comment = payload.comment
    post.updated_by = user.id
    post.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(post)
    log_action(db, "post", post.id, "reject", user.id, {"status": post.status, "comment": payload.comment})
    return post


@router.post("/{post_id}/schedule", response_model=PostOut)
def schedule_post(
    post_id: int,
    payload: ScheduleRequest,
    db: Session = Depends(get_db),
    _editor=Depends(require_roles(UserRole.editor, UserRole.admin)),
    user=Depends(get_current_user),
):
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if post.status not in {PostStatus.approved}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status")

    post.status = PostStatus.scheduled
    post.scheduled_at = payload.scheduled_at
    post.updated_by = user.id
    post.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(post)
    log_action(db, "post", post.id, "schedule", user.id, {"status": post.status, "scheduled_at": str(payload.scheduled_at)})
    return post


@router.post("/{post_id}/publish-now", response_model=PostOut)
def publish_now(
    post_id: int,
    db: Session = Depends(get_db),
    _editor=Depends(require_roles(UserRole.editor, UserRole.admin)),
    user=Depends(get_current_user),
):
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if post.status not in {PostStatus.approved, PostStatus.scheduled}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status")

    channel = db.get(Channel, post.channel_id)
    if not channel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")

    result = publish_message(
        channel.telegram_channel_identifier,
        f"{post.title}\n\n{post.body_text}",
        post.media_url,
    )
    if result.ok:
        post.status = PostStatus.published
        post.published_at = datetime.utcnow()
        post.telegram_message_id = result.message_id
        post.last_error = None
        post.updated_by = user.id
        post.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(post)
        log_action(db, "post", post.id, "publish", user.id, {"status": post.status})
        return post

    post.publish_attempts += 1
    post.updated_by = user.id
    post.updated_at = datetime.utcnow()
    post.last_error = result.error
    if post.publish_attempts < settings.publish_retry_max:
        post.status = PostStatus.scheduled
        post.scheduled_at = datetime.utcnow() + timedelta(seconds=settings.publish_retry_delay_seconds)
        db.commit()
        db.refresh(post)
        log_action(db, "post", post.id, "retry", user.id, {"error": result.error})
        return post

    post.status = PostStatus.failed
    db.commit()
    db.refresh(post)
    log_action(db, "post", post.id, "fail", user.id, {"error": result.error})
    return post
