from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.api.deps import get_current_user
from app.core.config import settings
from app.models.post import Post
from app.models.enums import PostStatus

router = APIRouter(prefix="", tags=["stats"])


@router.get("/channels/{channel_id}/stats")
def channel_stats(channel_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user)):
    posts = (
        db.query(Post)
        .filter(Post.channel_id == channel_id)
        .filter(Post.status == PostStatus.published)
        .order_by(Post.published_at.desc())
        .limit(10)
        .all()
    )
    views = [p.last_known_views for p in posts if p.last_known_views is not None]
    avg_views = int(sum(views) / len(views)) if views else None
    return {
        "channel_id": channel_id,
        "views_available": settings.telegram_feature_views,
        "subscribers": None,
        "avg_views_last_n": avg_views if settings.telegram_feature_views else None,
    }
