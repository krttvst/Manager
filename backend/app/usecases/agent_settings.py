from datetime import datetime
from sqlalchemy.orm import Session
from app.models.channel import Channel
from app.models.agent_settings import AgentSettings
from app.schemas.agent_settings import AgentSettingsIn
from app.repositories import agent_settings as settings_repo
from fastapi import HTTPException, status


def get_settings(db: Session, channel_id: int) -> AgentSettings | None:
    channel = db.get(Channel, channel_id)
    if not channel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")
    return settings_repo.get_by_channel(db, channel_id)


def upsert_settings(db: Session, channel_id: int, payload: AgentSettingsIn) -> AgentSettings:
    channel = db.get(Channel, channel_id)
    if not channel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")

    settings = settings_repo.get_by_channel(db, channel_id)
    if not settings:
        settings = AgentSettings(
            channel_id=channel_id,
            length=payload.length,
            style=payload.style,
            format=payload.format,
            temperature=payload.temperature,
            extra=payload.extra,
            tone_text=payload.tone_text,
            tone_values=payload.tone_values,
            updated_at=datetime.utcnow(),
        )
        return settings_repo.create(db, settings)

    settings.length = payload.length
    settings.style = payload.style
    settings.format = payload.format
    settings.temperature = payload.temperature
    settings.extra = payload.extra
    settings.tone_text = payload.tone_text
    settings.tone_values = payload.tone_values
    settings.updated_at = datetime.utcnow()
    return settings_repo.save(db, settings)
