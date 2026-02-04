from datetime import datetime
from sqlalchemy.orm import Session
from app.workers.celery_app import celery_app
from app.db.session import SessionLocal
from app.models.post import Post
from app.models.enums import PostStatus
from app.services.publisher import publish_post


@celery_app.task
def publish_scheduled_posts():
    db: Session = SessionLocal()
    try:
        now = datetime.utcnow()
        posts = (
            db.query(Post)
            .filter(Post.status == PostStatus.scheduled)
            .filter(Post.scheduled_at <= now)
            .with_for_update(skip_locked=True)
            .all()
        )
        for post in posts:
            actor_user_id = post.updated_by or post.created_by
            publish_post(db, post, actor_user_id)
    finally:
        db.close()
