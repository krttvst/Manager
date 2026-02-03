from datetime import datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.channel import Channel
from app.models.enums import PostStatus
from app.models.post import Post
from app.repositories import posts as post_repo
from app.schemas.post import PostCreate, PostUpdate, ScheduleRequest, RejectRequest
from app.services.audit import log_action
from app.services.telegram import publish_message, edit_message, delete_message


def create_post(db: Session, channel_id: int, payload: PostCreate, user) -> Post:
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
    post = post_repo.create_post(db, post)
    log_action(db, "post", post.id, "create", user.id, {"status": post.status})
    return post


def list_posts(db: Session, channel_id: int, status_filters, limit: int, offset: int) -> list[dict]:
    return post_repo.list_posts_compact(db, channel_id, status_filters, limit=limit, offset=offset)


def get_post(db: Session, post_id: int) -> Post:
    post = post_repo.get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post


def update_post(db: Session, post_id: int, payload: PostUpdate, user) -> Post:
    post = get_post(db, post_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(post, field, value)
    post.updated_by = user.id
    post.updated_at = datetime.utcnow()
    post = post_repo.save_post(db, post)
    log_action(db, "post", post.id, "update", user.id, {"status": post.status})

    if post.status == PostStatus.published and post.telegram_message_id:
        channel = db.get(Channel, post.channel_id)
        if not channel:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")
        edit_result = edit_message(
            channel.telegram_channel_identifier,
            post.telegram_message_id,
            f"{post.title}\n\n{post.body_text}",
            post.media_url,
        )
        if not edit_result.ok:
            post.last_error = edit_result.error
            post_repo.save_post(db, post)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=edit_result.error or "Edit failed")
    return post


def submit_approval(db: Session, post_id: int, user) -> Post:
    post = get_post(db, post_id)
    if post.status not in {PostStatus.draft, PostStatus.rejected}:
        return post

    post.status = PostStatus.pending
    post.updated_by = user.id
    post.updated_at = datetime.utcnow()
    post = post_repo.save_post(db, post)
    return post


def approve_post(db: Session, post_id: int, user) -> Post:
    post = get_post(db, post_id)
    if post.status != PostStatus.pending:
        return post

    post.status = PostStatus.approved
    post.editor_comment = None
    post.updated_by = user.id
    post.updated_at = datetime.utcnow()
    post = post_repo.save_post(db, post)
    log_action(db, "post", post.id, "approve", user.id, {"status": post.status})
    return post


def reject_post(db: Session, post_id: int, payload: RejectRequest, user) -> Post:
    post = get_post(db, post_id)
    if post.status != PostStatus.pending:
        return post

    post.status = PostStatus.rejected
    post.editor_comment = payload.comment
    post.updated_by = user.id
    post.updated_at = datetime.utcnow()
    post = post_repo.save_post(db, post)
    log_action(db, "post", post.id, "reject", user.id, {"status": post.status, "comment": payload.comment})
    return post


def schedule_post(db: Session, post_id: int, payload: ScheduleRequest, user) -> Post:
    post = get_post(db, post_id)
    if post.status in {PostStatus.draft, PostStatus.rejected}:
        post.status = PostStatus.pending
    if post.status == PostStatus.pending:
        post.status = PostStatus.approved
        post.editor_comment = None
    if post.status not in {PostStatus.approved, PostStatus.scheduled}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status")
    scheduled_at = payload.scheduled_at
    now = datetime.utcnow()
    if scheduled_at.tzinfo is not None:
        scheduled_at = scheduled_at.replace(tzinfo=None)
    if scheduled_at <= now:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Scheduled time must be in the future")

    post.status = PostStatus.scheduled
    post.scheduled_at = scheduled_at
    post.updated_by = user.id
    post.updated_at = datetime.utcnow()
    post = post_repo.save_post(db, post)
    log_action(db, "post", post.id, "schedule", user.id, {"status": post.status, "scheduled_at": str(payload.scheduled_at)})
    return post


def publish_now(db: Session, post_id: int, user) -> Post:
    post = get_post(db, post_id)
    if post.status in {PostStatus.draft, PostStatus.rejected}:
        post.status = PostStatus.pending
    if post.status == PostStatus.pending:
        post.status = PostStatus.approved
        post.editor_comment = None
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
        post = post_repo.save_post(db, post)
        log_action(db, "post", post.id, "publish", user.id, {"status": post.status})
        return post

    post.publish_attempts += 1
    post.updated_by = user.id
    post.updated_at = datetime.utcnow()
    post.last_error = result.error
    if post.publish_attempts < settings.publish_retry_max:
        post.status = PostStatus.scheduled
        post.scheduled_at = datetime.utcnow() + timedelta(seconds=settings.publish_retry_delay_seconds)
        post = post_repo.save_post(db, post)
        log_action(db, "post", post.id, "retry", user.id, {"error": result.error})
        return post

    post.status = PostStatus.failed
    post = post_repo.save_post(db, post)
    log_action(db, "post", post.id, "fail", user.id, {"error": result.error})
    return post


def delete_post(db: Session, post_id: int, user) -> None:
    post = get_post(db, post_id)
    if post.status == PostStatus.published and post.telegram_message_id:
        channel = db.get(Channel, post.channel_id)
        if not channel:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")
        delete_result = delete_message(channel.telegram_channel_identifier, post.telegram_message_id)
        if not delete_result.ok:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=delete_result.error or "Delete failed")
    post_repo.delete_source_items_for_post(db, post_id)
    post_repo.delete_post(db, post)
    log_action(db, "post", post_id, "delete", user.id, {})
