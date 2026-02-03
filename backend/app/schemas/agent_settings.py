from datetime import datetime
from pydantic import BaseModel


class AgentSettingsIn(BaseModel):
    length: int
    style: str
    format: str
    temperature: float
    extra: str | None = None
    tone_text: str | None = None
    tone_values: list[str] | None = None


class AgentSettingsOut(BaseModel):
    channel_id: int
    length: int
    style: str
    format: str
    temperature: float
    extra: str | None
    tone_text: str | None
    tone_values: list[str] | None = None
    updated_at: datetime

    class Config:
        from_attributes = True
