from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.channel import Channel
from app.models.post import Post
from app.models.enums import PostStatus
import logging
from app.services.telegram import publish_message
from app.services.audit import log_action
from app.metrics import PUBLISH_SUCCESS_TOTAL, PUBLISH_RETRY_TOTAL, PUBLISH_FAIL_TOTAL, POST_STATUS_TRANSITIONS_TOTAL


def publish_post(db: Session, post: Post, actor_user_id: int, channel: Channel | None = None) -> Post:
    logger = logging.getLogger("publisher")
    previous_status = post.status
    if post.status == PostStatus.published and post.telegram_message_id:
        return post
    if channel is None:
        channel = db.get(Channel, post.channel_id)
    if not channel:
        post.status = PostStatus.failed
        post.last_error = "Channel not found"
        post.updated_by = actor_user_id
        post.updated_at = datetime.utcnow()
        db.commit()
        PUBLISH_FAIL_TOTAL.inc()
        logger.warning("publish_fail", extra={"post_id": post.id, "error": post.last_error})
        log_action(db, "post", post.id, "fail", actor_user_id, {"error": post.last_error})
        db.commit()
        return post

    result = publish_message(
        channel.telegram_channel_identifier,
        f"{post.title}\n\n{post.body_text}",
        post.media_url,
    )
    now = datetime.utcnow()
    if result.ok:
        post.status = PostStatus.published
        post.published_at = now
        post.telegram_message_id = result.message_id
        post.last_error = None
        post.updated_by = actor_user_id
        post.updated_at = now
        db.commit()
        POST_STATUS_TRANSITIONS_TOTAL.labels(previous_status.value, post.status.value).inc()
        PUBLISH_SUCCESS_TOTAL.inc()
        logger.info("publish_success", extra={"post_id": post.id})
        log_action(db, "post", post.id, "publish", actor_user_id, {"status": post.status})
        db.commit()
        return post

    if not result.retryable:
        post.status = PostStatus.failed
        post.last_error = result.error
        post.updated_by = actor_user_id
        post.updated_at = now
        db.commit()
        POST_STATUS_TRANSITIONS_TOTAL.labels(previous_status.value, post.status.value).inc()
        PUBLISH_FAIL_TOTAL.inc()
        logger.warning("publish_fail", extra={"post_id": post.id, "error": result.error, "retryable": False})
        log_action(db, "post", post.id, "fail", actor_user_id, {"error": result.error, "retryable": False})
        db.commit()
        return post

    post.publish_attempts += 1
    post.last_error = result.error
    post.updated_by = actor_user_id
    post.updated_at = now
    if post.publish_attempts < settings.publish_retry_max:
        post.status = PostStatus.scheduled
        post.scheduled_at = now + timedelta(seconds=settings.publish_retry_delay_seconds)
        db.commit()
        POST_STATUS_TRANSITIONS_TOTAL.labels(previous_status.value, post.status.value).inc()
        PUBLISH_RETRY_TOTAL.inc()
        logger.info("publish_retry", extra={"post_id": post.id, "error": result.error})
        log_action(db, "post", post.id, "retry", actor_user_id, {"error": result.error})
        db.commit()
        return post

    post.status = PostStatus.failed
    db.commit()
    POST_STATUS_TRANSITIONS_TOTAL.labels(previous_status.value, post.status.value).inc()
    PUBLISH_FAIL_TOTAL.inc()
    logger.warning("publish_fail", extra={"post_id": post.id, "error": result.error})
    log_action(db, "post", post.id, "fail", actor_user_id, {"error": result.error})
    db.commit()
    return post
