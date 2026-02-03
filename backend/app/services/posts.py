from sqlalchemy.orm import Session

from app.usecases import posts as post_usecase
from app.schemas.post import PostCreate, PostUpdate, ScheduleRequest, RejectRequest
from app.models.enums import PostStatus
from app.models.post import Post


# Backwards-compatible service wrappers delegating to use-cases.

def create_post(db: Session, channel_id: int, payload: PostCreate, user) -> Post:
    return post_usecase.create_post(db, channel_id, payload, user)


def list_posts(db: Session, channel_id: int, status_filter: PostStatus | None, limit: int = 50, offset: int = 0):
    return post_usecase.list_posts(db, channel_id, status_filter, limit=limit, offset=offset)


def get_post(db: Session, post_id: int) -> Post:
    return post_usecase.get_post(db, post_id)


def update_post(db: Session, post_id: int, payload: PostUpdate, user) -> Post:
    return post_usecase.update_post(db, post_id, payload, user)


def submit_approval(db: Session, post_id: int, user) -> Post:
    return post_usecase.submit_approval(db, post_id, user)


def approve_post(db: Session, post_id: int, user) -> Post:
    return post_usecase.approve_post(db, post_id, user)


def reject_post(db: Session, post_id: int, payload: RejectRequest, user) -> Post:
    return post_usecase.reject_post(db, post_id, payload, user)


def schedule_post(db: Session, post_id: int, payload: ScheduleRequest, user) -> Post:
    return post_usecase.schedule_post(db, post_id, payload, user)


def publish_now(db: Session, post_id: int, user) -> Post:
    return post_usecase.publish_now(db, post_id, user)


def delete_post(db: Session, post_id: int, user) -> None:
    return post_usecase.delete_post(db, post_id, user)
