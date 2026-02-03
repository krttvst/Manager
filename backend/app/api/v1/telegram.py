from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.usecases import channels as channel_usecase

router = APIRouter(prefix="/telegram", tags=["telegram"])


@router.post("/webhook")
async def telegram_webhook(request: Request, db: Session = Depends(get_db)):
    update = await request.json()
    payload = update.get("my_chat_member") or update.get("chat_member")
    if not payload:
        return {"ok": True}

    chat = payload.get("chat") or {}
    new_member = payload.get("new_chat_member") or {}
    status = new_member.get("status")
    chat_type = chat.get("type")
    if status != "administrator" or chat_type != "channel":
        return {"ok": True}

    chat_id = chat.get("id")
    if chat_id is None:
        return {"ok": True}

    username = chat.get("username")
    title = chat.get("title")
    channel_usecase.auto_add_channel_from_telegram(db, str(chat_id), username, title)
    return {"ok": True}
