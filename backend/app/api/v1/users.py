from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.api.deps import get_current_user, require_roles
from app.models.enums import UserRole
from app.schemas.user import UserOut, UserCreate
from app.core.security import hash_password
from app.models.user import User

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
def me(current_user=Depends(get_current_user)):
    return current_user


@router.post("/", response_model=UserOut)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    _admin=Depends(require_roles(UserRole.admin)),
):
    user = User(email=payload.email, password_hash=hash_password(payload.password), role=payload.role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
