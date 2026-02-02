from sqlalchemy.orm import Session
from app.core.security import hash_password
from app.models.user import User
from app.models.enums import UserRole


def init_admin(db: Session, email: str, password: str) -> User:
    user = db.query(User).filter(User.email == email).first()
    if user:
        return user
    user = User(email=email, password_hash=hash_password(password), role=UserRole.admin)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
