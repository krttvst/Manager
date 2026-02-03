from sqlalchemy.orm import Session
from app.models.agent_settings import AgentSettings


def get_by_channel(db: Session, channel_id: int) -> AgentSettings | None:
    return db.query(AgentSettings).filter(AgentSettings.channel_id == channel_id).first()


def create(db: Session, settings: AgentSettings) -> AgentSettings:
    db.add(settings)
    db.commit()
    db.refresh(settings)
    return settings


def save(db: Session, settings: AgentSettings) -> AgentSettings:
    db.add(settings)
    db.commit()
    db.refresh(settings)
    return settings
