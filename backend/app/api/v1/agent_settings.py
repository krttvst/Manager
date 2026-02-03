from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.api.deps import get_current_user
from app.schemas.agent_settings import AgentSettingsIn, AgentSettingsOut
from app.usecases import agent_settings as settings_usecase

router = APIRouter(prefix="", tags=["agent-settings"])


@router.get("/channels/{channel_id}/agent-settings", response_model=AgentSettingsOut | None)
def get_agent_settings(
    channel_id: int,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    return settings_usecase.get_settings(db, channel_id)


@router.put("/channels/{channel_id}/agent-settings", response_model=AgentSettingsOut)
def update_agent_settings(
    channel_id: int,
    payload: AgentSettingsIn,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    return settings_usecase.upsert_settings(db, channel_id, payload)
