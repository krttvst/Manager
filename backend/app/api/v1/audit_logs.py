from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.db.deps import get_db
from app.models.enums import UserRole
from app.schemas.audit_log import AuditLogListOut, AuditLogOut
from app.usecases import audit_logs as audit_usecase

router = APIRouter(prefix="/audit-logs", tags=["audit"])


@router.get("", response_model=AuditLogListOut)
def list_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    entity_type: str | None = None,
    entity_id: int | None = None,
    actor_user_id: int | None = None,
    action: str | None = None,
    since: datetime | None = None,
    until: datetime | None = None,
    db: Session = Depends(get_db),
    _admin=Depends(require_roles(UserRole.admin)),
):
    return audit_usecase.list_audit_logs(
        db,
        limit=limit,
        offset=offset,
        entity_type=entity_type,
        entity_id=entity_id,
        actor_user_id=actor_user_id,
        action=action,
        since=since,
        until=until,
    )


@router.get("/{audit_id}", response_model=AuditLogOut)
def get_audit_log(
    audit_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(require_roles(UserRole.admin)),
):
    return audit_usecase.get_audit_log(db, audit_id)

