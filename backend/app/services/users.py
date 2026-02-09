from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import hash_password
import secrets
from app.services.audit import log_action


def create_user(db: Session, payload: UserCreate) -> User:
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
    user = User(email=payload.email, password_hash=hash_password(payload.password), role=payload.role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def list_users(db: Session, *, limit: int = 50, offset: int = 0, q: str | None = None) -> tuple[list[User], int]:
    safe_limit = max(1, min(int(limit), 200))
    safe_offset = max(0, int(offset))
    base = db.query(User)
    if q:
        like = f"%{q.strip()}%"
        base = base.filter(User.email.ilike(like))
    # Using Query.count() avoids cross-dialect quirks with with_entities(func.count()).
    total = base.order_by(None).count()
    items = base.order_by(User.created_at.desc()).limit(safe_limit).offset(safe_offset).all()
    return items, int(total)


def update_user_role(db: Session, *, user_id: int, role) -> User:
    user = db.get(User, int(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.role = role
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def set_user_password(db: Session, *, user_id: int, password: str) -> User:
    user = db.get(User, int(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not password:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Password is required")
    user.password_hash = hash_password(password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def set_user_active(db: Session, *, user_id: int, is_active: bool) -> User:
    user = db.get(User, int(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.is_active = bool(is_active)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def reset_user_password(db: Session, *, user_id: int, actor_user_id: int) -> tuple[User, str]:
    user = db.get(User, int(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    # 16-ish chars, URL-safe, good enough for a temporary password.
    temp_password = secrets.token_urlsafe(12)
    user.password_hash = hash_password(temp_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    log_action(db, "user", user.id, "reset_password", actor_user_id, {"email": user.email})
    return user, temp_password
