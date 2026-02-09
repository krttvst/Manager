from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog


def log_action(db: Session, entity_type: str, entity_id: int, action: str, actor_user_id: int, payload: dict) -> None:
    # Intentionally does not commit.
    # Callers should commit as part of their transaction boundary to avoid
    # surprising partial commits from this helper.
    entry = AuditLog(
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        actor_user_id=actor_user_id,
        payload_json=payload,
    )
    db.add(entry)
