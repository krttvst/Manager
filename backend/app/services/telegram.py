from dataclasses import dataclass
import httpx
from app.core.config import settings


@dataclass
class TelegramResult:
    ok: bool
    message_id: str | None
    error: str | None


def publish_message(channel_identifier: str, text: str, photo_url: str | None = None) -> TelegramResult:
    if not settings.telegram_bot_token:
        return TelegramResult(ok=False, message_id=None, error="Bot token not configured")

    base_url = f"https://api.telegram.org/bot{settings.telegram_bot_token}"
    payload = {"chat_id": channel_identifier, "caption": text} if photo_url else {"chat_id": channel_identifier, "text": text}
    endpoint = "/sendPhoto" if photo_url else "/sendMessage"

    try:
        with httpx.Client(timeout=10) as client:
            if photo_url:
                payload["photo"] = photo_url
            response = client.post(base_url + endpoint, json=payload)
            response.raise_for_status()
            data = response.json()
    except Exception as exc:
        return TelegramResult(ok=False, message_id=None, error=str(exc))

    if not data.get("ok"):
        return TelegramResult(ok=False, message_id=None, error=str(data))

    message_id = data.get("result", {}).get("message_id")
    return TelegramResult(ok=True, message_id=str(message_id) if message_id else None, error=None)
