from datetime import datetime

from pydantic import BaseModel


class AuditLogOut(BaseModel):
    id: int
    entity_type: str
    entity_id: int
    action: str
    actor_user_id: int
    actor_email: str | None = None
    payload_json: dict
    created_at: datetime


class AuditLogListOut(BaseModel):
    items: list[AuditLogOut]
    total: int
    limit: int
    offset: int

