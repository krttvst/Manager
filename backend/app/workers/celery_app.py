import os
from celery import Celery

broker_url = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
backend_url = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")

celery_app = Celery(
    "manager_tg",
    broker=broker_url,
    backend=backend_url,
)

celery_app.conf.update(
    task_track_started=True,
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "publish-scheduled-posts-every-minute": {
            "task": "app.workers.tasks.publish_scheduled_posts",
            "schedule": 60.0,
        }
    },
)
