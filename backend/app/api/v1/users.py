from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.api.deps import get_current_user, require_roles
from app.models.enums import UserRole
from app.schemas.user import (
    UserOut,
    UserCreate,
    UsersListOut,
    UserRoleUpdate,
    UserPasswordUpdate,
    UserActiveUpdate,
    UserPasswordResetOut,
)
from app.services import users as user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
def me(current_user=Depends(get_current_user)):
    return current_user


@router.post("/", response_model=UserOut)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_roles(UserRole.admin)),
):
    return user_service.create_user(db, payload, actor_user_id=admin.id)


@router.get("", response_model=UsersListOut)
def list_users(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    q: str | None = None,
    db: Session = Depends(get_db),
    _admin=Depends(require_roles(UserRole.admin)),
):
    items, total = user_service.list_users(db, limit=limit, offset=offset, q=q)
    return UsersListOut(items=items, total=total, limit=limit, offset=offset)


@router.patch("/{user_id}/role", response_model=UserOut)
def update_role(
    user_id: int,
    payload: UserRoleUpdate,
    db: Session = Depends(get_db),
    admin=Depends(require_roles(UserRole.admin)),
):
    return user_service.update_user_role(db, user_id=user_id, role=payload.role, actor_user_id=admin.id)


@router.patch("/{user_id}/password", response_model=UserOut)
def update_password(
    user_id: int,
    payload: UserPasswordUpdate,
    db: Session = Depends(get_db),
    admin=Depends(require_roles(UserRole.admin)),
):
    return user_service.set_user_password(db, user_id=user_id, password=payload.password, actor_user_id=admin.id)


@router.patch("/{user_id}/active", response_model=UserOut)
def update_active(
    user_id: int,
    payload: UserActiveUpdate,
    db: Session = Depends(get_db),
    admin=Depends(require_roles(UserRole.admin)),
):
    return user_service.set_user_active(db, user_id=user_id, is_active=payload.is_active, actor_user_id=admin.id)


@router.post("/{user_id}/reset-password", response_model=UserPasswordResetOut)
def reset_password(
    user_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_roles(UserRole.admin)),
):
    _user, temp_password = user_service.reset_user_password(db, user_id=user_id, actor_user_id=admin.id)
    return UserPasswordResetOut(temporary_password=temp_password)
