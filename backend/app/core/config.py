from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_env: str = "development"
    app_secret: str = "change_me"

    database_url: str

    access_token_expire_minutes: int = 60

    telegram_bot_token: str | None = None
    telegram_feature_views: bool = False

    redis_url: str = "redis://redis:6379/0"
    celery_broker_url: str = "redis://redis:6379/0"
    celery_result_backend: str = "redis://redis:6379/0"

    publish_retry_max: int = 3
    publish_retry_delay_seconds: int = 300

    media_dir: str = "/app/media"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
