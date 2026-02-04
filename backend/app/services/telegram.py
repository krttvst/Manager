from dataclasses import dataclass
from pathlib import Path
import json
import time
import httpx
from app.core.config import settings
from app.metrics import TELEGRAM_ERRORS_TOTAL


@dataclass
class TelegramResult:
    ok: bool
    message_id: str | None
    error: str | None
    retryable: bool = False


def _local_media_path(photo_url: str) -> Path:
    filename = photo_url.split("/media/", 1)[1]
    return Path(settings.media_dir) / filename


def _base_url() -> str:
    if not settings.telegram_bot_token:
        raise ValueError("Bot token not configured")
    return f"https://api.telegram.org/bot{settings.telegram_bot_token}"


def _client() -> httpx.Client:
    return httpx.Client(timeout=settings.telegram_timeout_seconds)


def _is_retryable_error(exc: Exception) -> bool:
    if isinstance(exc, httpx.TimeoutException):
        return True
    if isinstance(exc, httpx.NetworkError):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        status = exc.response.status_code
        return status == 429 or status >= 500
    return False


def _backoff(attempt: int) -> None:
    time.sleep(0.5 * (2 ** attempt))


def _request_with_retries(method: str, url: str, *, action: str, data=None, json=None, files=None, params=None) -> dict:
    last_exc: Exception | None = None
    for attempt in range(settings.telegram_retries + 1):
        try:
            with _client() as client:
                response = client.request(method, url, data=data, json=json, files=files, params=params)
            response.raise_for_status()
            try:
                return response.json()
            except Exception:
                return {"ok": False, "description": response.text}
        except Exception as exc:
            last_exc = exc
            if attempt >= settings.telegram_retries or not _is_retryable_error(exc):
                break
            _backoff(attempt)
    if last_exc is None:
        TELEGRAM_ERRORS_TOTAL.labels(action, "false").inc()
        return {"ok": False, "description": "Unknown error"}
    retryable = _is_retryable_error(last_exc)
    TELEGRAM_ERRORS_TOTAL.labels(action, "true" if retryable else "false").inc()
    return {"ok": False, "description": str(last_exc), "retryable": retryable}


def _download_bytes_with_retries(url: str) -> bytes | None:
    last_exc: Exception | None = None
    for attempt in range(settings.telegram_retries + 1):
        try:
            with _client() as client:
                response = client.get(url)
            response.raise_for_status()
            return response.content
        except Exception as exc:
            last_exc = exc
            if attempt >= settings.telegram_retries or not _is_retryable_error(exc):
                break
            _backoff(attempt)
    if last_exc is not None:
        retryable = _is_retryable_error(last_exc)
        TELEGRAM_ERRORS_TOTAL.labels("downloadFile", "true" if retryable else "false").inc()
    return None


def _file_url(file_path: str) -> str:
    return f"https://api.telegram.org/file/bot{settings.telegram_bot_token}/{file_path}"


def _normalize_identifier(identifier: str) -> str:
    value = str(identifier).strip()
    if value.startswith("https://t.me/"):
        value = value.replace("https://t.me/", "", 1)
    elif value.startswith("http://t.me/"):
        value = value.replace("http://t.me/", "", 1)
    elif value.startswith("t.me/"):
        value = value.replace("t.me/", "", 1)
    if value.lstrip("-").isdigit():
        return value
    if not value.startswith("@"):
        value = f"@{value}"
    return value


def _get_chat(chat_id_or_username: str) -> dict:
    base_url = _base_url()
    data = _request_with_retries("GET", f"{base_url}/getChat", action="getChat", params={"chat_id": chat_id_or_username})
    if not data.get("ok"):
        raise ValueError(str(data))
    return data.get("result", {})


def lookup_channel_profile(identifier: str) -> dict:
    if not settings.telegram_bot_token:
        raise ValueError("Bot token not configured")
    chat_id = _normalize_identifier(identifier)
    result = _get_chat(chat_id)
    title = result.get("title") or chat_id
    photo = result.get("photo") or {}
    file_id = photo.get("big_file_id") or photo.get("small_file_id")
    avatar_url = None
    if file_id:
        avatar_url = _download_avatar(file_id)
    return {"title": title, "avatar_url": avatar_url}


def _download_avatar(file_id: str) -> str | None:
    base_url = _base_url()
    file_data = _request_with_retries("GET", f"{base_url}/getFile", action="getFile", params={"file_id": file_id})
    if not file_data.get("ok"):
        return None
    file_path = file_data.get("result", {}).get("file_path")
    if not file_path:
        return None
    file_url = _file_url(file_path)
    content = _download_bytes_with_retries(file_url)
    if content is None:
        return None

    extension = Path(file_path).suffix or ".jpg"
    avatars_dir = Path(settings.media_dir) / "avatars"
    avatars_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{file_id}{extension}"
    target = avatars_dir / filename
    if not target.exists():
        target.write_bytes(content)
    return f"/media/avatars/{filename}"


def publish_message(channel_identifier: str, text: str, photo_url: str | None = None) -> TelegramResult:
    if not settings.telegram_bot_token:
        return TelegramResult(ok=False, message_id=None, error="Bot token not configured")

    base_url = f"https://api.telegram.org/bot{settings.telegram_bot_token}"
    payload = {"chat_id": channel_identifier, "caption": text} if photo_url else {"chat_id": channel_identifier, "text": text}
    endpoint = "/sendPhoto" if photo_url else "/sendMessage"

    if photo_url and photo_url.startswith("/media/"):
        filename = photo_url.split("/media/", 1)[1]
        file_path = Path(settings.media_dir) / filename
        if not file_path.exists():
            return TelegramResult(ok=False, message_id=None, error="Media file not found")
        with file_path.open("rb") as file_obj:
            data = _request_with_retries(
                "POST",
                base_url + endpoint,
                action="sendPhoto",
                data={"chat_id": channel_identifier, "caption": text},
                files={"photo": file_obj},
            )
    else:
        if photo_url:
            payload["photo"] = photo_url
        data = _request_with_retries("POST", base_url + endpoint, action="sendMessage", json=payload)

    if not data.get("ok"):
        return TelegramResult(
            ok=False,
            message_id=None,
            error=str(data.get("description") or data),
            retryable=bool(data.get("retryable")),
        )

    message_id = data.get("result", {}).get("message_id")
    return TelegramResult(ok=True, message_id=str(message_id) if message_id else None, error=None)


def edit_message(channel_identifier: str, message_id: str, text: str, photo_url: str | None = None) -> TelegramResult:
    if not settings.telegram_bot_token:
        return TelegramResult(ok=False, message_id=None, error="Bot token not configured")

    base_url = f"https://api.telegram.org/bot{settings.telegram_bot_token}"

    if photo_url:
        if photo_url.startswith("/media/"):
            file_path = _local_media_path(photo_url)
            if not file_path.exists():
                return TelegramResult(ok=False, message_id=None, error="Media file not found")
            media = {
                "type": "photo",
                "media": "attach://photo",
                "caption": text,
            }
            with file_path.open("rb") as file_obj:
                data = _request_with_retries(
                    "POST",
                    base_url + "/editMessageMedia",
                    action="editMessageMedia",
                    data={"chat_id": channel_identifier, "message_id": message_id, "media": json.dumps(media)},
                    files={"photo": file_obj},
                )
        else:
            media = {"type": "photo", "media": photo_url, "caption": text}
            data = _request_with_retries(
                "POST",
                base_url + "/editMessageMedia",
                action="editMessageMedia",
                json={"chat_id": channel_identifier, "message_id": message_id, "media": media},
            )
    else:
        data = _request_with_retries(
            "POST",
            base_url + "/editMessageText",
            action="editMessageText",
            json={"chat_id": channel_identifier, "message_id": message_id, "text": text},
        )

    if not data.get("ok"):
        description = str(data.get("description") or data)
        if "message is not modified" in description.lower():
            return TelegramResult(ok=True, message_id=str(message_id), error=None)
        return TelegramResult(
            ok=False,
            message_id=None,
            error=description,
            retryable=bool(data.get("retryable")),
        )

    return TelegramResult(ok=True, message_id=str(message_id), error=None)


def delete_message(channel_identifier: str, message_id: str) -> TelegramResult:
    if not settings.telegram_bot_token:
        return TelegramResult(ok=False, message_id=None, error="Bot token not configured")

    base_url = f"https://api.telegram.org/bot{settings.telegram_bot_token}"
    data = _request_with_retries(
        "POST",
        base_url + "/deleteMessage",
        action="deleteMessage",
        json={"chat_id": channel_identifier, "message_id": message_id},
    )

    if not data.get("ok"):
        return TelegramResult(
            ok=False,
            message_id=None,
            error=str(data.get("description") or data),
            retryable=bool(data.get("retryable")),
        )

    return TelegramResult(ok=True, message_id=str(message_id), error=None)


def get_message_views(channel_identifier: str, message_id: str) -> int | None:
    if not settings.telegram_bot_token:
        return None

    base_url = _base_url()
    data = _request_with_retries(
        "GET",
        f"{base_url}/getMessage",
        action="getMessage",
        params={"chat_id": channel_identifier, "message_id": message_id},
    )

    if not data.get("ok"):
        return None

    result = data.get("result", {})
    views = result.get("views") or result.get("view_count")
    try:
        return int(views) if views is not None else None
    except Exception:
        return None
