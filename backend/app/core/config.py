from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_env: str = "development"
    app_secret: str = "change_me"

    database_url: str

    access_token_expire_minutes: int = 60

    telegram_bot_token: str | None = None
    telegram_feature_views: bool = False
    telegram_webhook_secret: str | None = None
    n8n_api_key: str | None = None
    telegram_timeout_seconds: int = 10
    telegram_retries: int = 2

    redis_url: str = "redis://redis:6379/0"
    celery_broker_url: str = "redis://redis:6379/0"
    celery_result_backend: str = "redis://redis:6379/0"
    rate_limit_enabled: bool = True
    rate_limit_redis_url: str | None = None
    metrics_enabled: bool = True

    publish_retry_max: int = 3
    publish_retry_delay_seconds: int = 300

    media_dir: str = "/app/media"
    media_max_bytes: int = 5 * 1024 * 1024
    media_max_pixels: int = 30_000_000

    @model_validator(mode="after")
    def _validate_secrets(self):
        if self.app_env.lower() == "production" and self.app_secret == "change_me":
            raise ValueError("APP_SECRET must be set in production")
        if self.rate_limit_enabled and not (self.rate_limit_redis_url or self.redis_url):
            raise ValueError("Rate limiting enabled but Redis URL is missing")
        return self

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
