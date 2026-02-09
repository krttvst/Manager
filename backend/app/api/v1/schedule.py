from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.deps import get_db
from app.models.enums import UserRole
from app.schemas.post import PostOut
from app.schemas.schedule import ScheduledPostListOut, RequeueRequest
from app.usecases import schedule as schedule_usecase
from app.usecases import posts as posts_usecase

router = APIRouter(prefix="/schedule", tags=["schedule"])


@router.get("", response_model=ScheduledPostListOut)
def list_schedule(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    channel_id: int | None = None,
    since: datetime | None = None,
    until: datetime | None = None,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    return schedule_usecase.list_scheduled_posts(
        db,
        limit=limit,
        offset=offset,
        channel_id=channel_id,
        since=since,
        until=until,
    )


@router.post("/posts/{post_id}/requeue", response_model=PostOut)
def requeue_post(
    post_id: int,
    payload: RequeueRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
    _editor=Depends(require_roles(UserRole.editor, UserRole.admin)),
):
    schedule_usecase.requeue_failed_post(db, post_id=post_id, actor_user_id=user.id, delay_seconds=payload.delay_seconds)
    return posts_usecase.get_post(db, post_id)

