from dataclasses import dataclass
from pathlib import Path
import json
import httpx
from app.core.config import settings


@dataclass
class TelegramResult:
    ok: bool
    message_id: str | None
    error: str | None


def _local_media_path(photo_url: str) -> Path:
    filename = photo_url.split("/media/", 1)[1]
    return Path(settings.media_dir) / filename


def _base_url() -> str:
    if not settings.telegram_bot_token:
        raise ValueError("Bot token not configured")
    return f"https://api.telegram.org/bot{settings.telegram_bot_token}"


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
    with httpx.Client(timeout=10) as client:
        response = client.get(f"{base_url}/getChat", params={"chat_id": chat_id_or_username})
        response.raise_for_status()
        data = response.json()
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
    with httpx.Client(timeout=10) as client:
        file_resp = client.get(f"{base_url}/getFile", params={"file_id": file_id})
        file_resp.raise_for_status()
        file_data = file_resp.json()
        if not file_data.get("ok"):
            return None
        file_path = file_data.get("result", {}).get("file_path")
        if not file_path:
            return None
        file_url = _file_url(file_path)
        download = client.get(file_url)
        download.raise_for_status()

    extension = Path(file_path).suffix or ".jpg"
    avatars_dir = Path(settings.media_dir) / "avatars"
    avatars_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{file_id}{extension}"
    target = avatars_dir / filename
    if not target.exists():
        target.write_bytes(download.content)
    return f"/media/avatars/{filename}"


def publish_message(channel_identifier: str, text: str, photo_url: str | None = None) -> TelegramResult:
    if not settings.telegram_bot_token:
        return TelegramResult(ok=False, message_id=None, error="Bot token not configured")

    base_url = f"https://api.telegram.org/bot{settings.telegram_bot_token}"
    payload = {"chat_id": channel_identifier, "caption": text} if photo_url else {"chat_id": channel_identifier, "text": text}
    endpoint = "/sendPhoto" if photo_url else "/sendMessage"

    try:
        with httpx.Client(timeout=10) as client:
            if photo_url:
                if photo_url.startswith("/media/"):
                    filename = photo_url.split("/media/", 1)[1]
                    file_path = Path(settings.media_dir) / filename
                    if not file_path.exists():
                        return TelegramResult(ok=False, message_id=None, error="Media file not found")
                    with file_path.open("rb") as file_obj:
                        response = client.post(
                            base_url + endpoint,
                            data={"chat_id": channel_identifier, "caption": text},
                            files={"photo": file_obj},
                        )
                else:
                    payload["photo"] = photo_url
                    response = client.post(base_url + endpoint, json=payload)
            else:
                response = client.post(base_url + endpoint, json=payload)
            response.raise_for_status()
            data = response.json()
    except Exception as exc:
        return TelegramResult(ok=False, message_id=None, error=str(exc))

    if not data.get("ok"):
        return TelegramResult(ok=False, message_id=None, error=str(data))

    message_id = data.get("result", {}).get("message_id")
    return TelegramResult(ok=True, message_id=str(message_id) if message_id else None, error=None)


def edit_message(channel_identifier: str, message_id: str, text: str, photo_url: str | None = None) -> TelegramResult:
    if not settings.telegram_bot_token:
        return TelegramResult(ok=False, message_id=None, error="Bot token not configured")

    base_url = f"https://api.telegram.org/bot{settings.telegram_bot_token}"

    try:
        with httpx.Client(timeout=10) as client:
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
                        response = client.post(
                            base_url + "/editMessageMedia",
                            data={"chat_id": channel_identifier, "message_id": message_id, "media": json.dumps(media)},
                            files={"photo": file_obj},
                        )
                else:
                    media = {"type": "photo", "media": photo_url, "caption": text}
                    response = client.post(
                        base_url + "/editMessageMedia",
                        json={"chat_id": channel_identifier, "message_id": message_id, "media": media},
                    )
            else:
                response = client.post(
                    base_url + "/editMessageText",
                    json={"chat_id": channel_identifier, "message_id": message_id, "text": text},
                )
            try:
                data = response.json()
            except Exception:
                data = {"ok": False, "description": response.text}
    except Exception as exc:
        return TelegramResult(ok=False, message_id=None, error=str(exc))

    if not data.get("ok"):
        description = str(data.get("description") or data)
        if "message is not modified" in description.lower():
            return TelegramResult(ok=True, message_id=str(message_id), error=None)
        return TelegramResult(ok=False, message_id=None, error=description)

    return TelegramResult(ok=True, message_id=str(message_id), error=None)


def delete_message(channel_identifier: str, message_id: str) -> TelegramResult:
    if not settings.telegram_bot_token:
        return TelegramResult(ok=False, message_id=None, error="Bot token not configured")

    base_url = f"https://api.telegram.org/bot{settings.telegram_bot_token}"
    try:
        with httpx.Client(timeout=10) as client:
            response = client.post(
                base_url + "/deleteMessage",
                json={"chat_id": channel_identifier, "message_id": message_id},
            )
            response.raise_for_status()
            data = response.json()
    except Exception as exc:
        return TelegramResult(ok=False, message_id=None, error=str(exc))

    if not data.get("ok"):
        return TelegramResult(ok=False, message_id=None, error=str(data))

    return TelegramResult(ok=True, message_id=str(message_id), error=None)
