from __future__ import annotations

from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.audit_log import AuditLogListOut, AuditLogOut

MAX_LIMIT = 200


def list_audit_logs(
    db: Session,
    *,
    limit: int = 50,
    offset: int = 0,
    entity_type: str | None = None,
    entity_id: int | None = None,
    actor_user_id: int | None = None,
    action: str | None = None,
    since: datetime | None = None,
    until: datetime | None = None,
) -> AuditLogListOut:
    safe_limit = max(1, min(int(limit), MAX_LIMIT))
    safe_offset = max(0, int(offset))

    stmt = (
        select(
            AuditLog.id,
            AuditLog.entity_type,
            AuditLog.entity_id,
            AuditLog.action,
            AuditLog.actor_user_id,
            User.email.label("actor_email"),
            AuditLog.payload_json,
            AuditLog.created_at,
        )
        .select_from(AuditLog)
        .join(User, User.id == AuditLog.actor_user_id, isouter=True)
    )
    count_stmt = select(func.count()).select_from(AuditLog)

    def apply_filters(s):
        if entity_type:
            s = s.where(AuditLog.entity_type == entity_type)
        if entity_id is not None:
            s = s.where(AuditLog.entity_id == int(entity_id))
        if actor_user_id is not None:
            s = s.where(AuditLog.actor_user_id == int(actor_user_id))
        if action:
            s = s.where(AuditLog.action == action)
        if since is not None:
            s = s.where(AuditLog.created_at >= since)
        if until is not None:
            s = s.where(AuditLog.created_at <= until)
        return s

    stmt = apply_filters(stmt)
    count_stmt = apply_filters(count_stmt)

    total = db.execute(count_stmt).scalar_one()
    rows = db.execute(stmt.order_by(AuditLog.created_at.desc()).limit(safe_limit).offset(safe_offset)).all()

    items = [
        AuditLogOut(
            id=int(r.id),
            entity_type=r.entity_type,
            entity_id=int(r.entity_id),
            action=r.action,
            actor_user_id=int(r.actor_user_id),
            actor_email=getattr(r, "actor_email", None),
            payload_json=r.payload_json,
            created_at=r.created_at,
        )
        for r in rows
    ]

    return AuditLogListOut(items=items, total=int(total), limit=safe_limit, offset=safe_offset)


def get_audit_log(db: Session, audit_id: int) -> AuditLogOut:
    row = db.execute(
        select(
            AuditLog.id,
            AuditLog.entity_type,
            AuditLog.entity_id,
            AuditLog.action,
            AuditLog.actor_user_id,
            User.email.label("actor_email"),
            AuditLog.payload_json,
            AuditLog.created_at,
        )
        .select_from(AuditLog)
        .join(User, User.id == AuditLog.actor_user_id, isouter=True)
        .where(AuditLog.id == int(audit_id))
    ).first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audit log not found")
    r = row._mapping
    return AuditLogOut(
        id=int(r["id"]),
        entity_type=r["entity_type"],
        entity_id=int(r["entity_id"]),
        action=r["action"],
        actor_user_id=int(r["actor_user_id"]),
        actor_email=r.get("actor_email"),
        payload_json=r["payload_json"],
        created_at=r["created_at"],
    )

