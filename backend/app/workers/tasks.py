from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.workers.celery_app import celery_app
from app.db.session import SessionLocal
from app.models.post import Post
from app.models.channel import Channel
from app.models.enums import PostStatus
from app.services.telegram import publish_message
from app.services.audit import log_action
from app.core.config import settings


@celery_app.task
def publish_scheduled_posts():
    db: Session = SessionLocal()
    try:
        now = datetime.utcnow()
        max_attempts = settings.publish_retry_max
        retry_delay = settings.publish_retry_delay_seconds
        posts = (
            db.query(Post)
            .filter(Post.status == PostStatus.scheduled)
            .filter(Post.scheduled_at <= now)
            .all()
        )
        for post in posts:
            channel = db.get(Channel, post.channel_id)
            if not channel:
                post.status = PostStatus.failed
                post.last_error = "Channel not found"
                db.commit()
                continue

            result = publish_message(channel.telegram_channel_identifier, f"{post.title}\n\n{post.body_text}", post.media_url)
            if result.ok:
                post.status = PostStatus.published
                post.published_at = datetime.utcnow()
                post.telegram_message_id = result.message_id
                post.updated_at = datetime.utcnow()
                post.last_error = None
                db.commit()
                log_action(db, "post", post.id, "publish", post.updated_by, {"status": post.status})
            else:
                post.publish_attempts += 1
                post.updated_at = datetime.utcnow()
                post.last_error = result.error
                if post.publish_attempts < max_attempts:
                    post.status = PostStatus.scheduled
                    post.scheduled_at = datetime.utcnow() + timedelta(seconds=retry_delay)
                    db.commit()
                    log_action(
                        db,
                        "post",
                        post.id,
                        "retry",
                        post.updated_by,
                        {"error": result.error, "attempt": post.publish_attempts},
                    )
                else:
                    post.status = PostStatus.failed
                    db.commit()
                    log_action(db, "post", post.id, "fail", post.updated_by, {"error": result.error})
    finally:
        db.close()
