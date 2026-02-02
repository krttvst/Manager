from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog


def log_action(db: Session, entity_type: str, entity_id: int, action: str, actor_user_id: int, payload: dict) -> None:
    entry = AuditLog(
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        actor_user_id=actor_user_id,
        payload_json=payload,
    )
    db.add(entry)
    db.commit()
