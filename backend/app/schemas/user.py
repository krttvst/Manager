from datetime import datetime
from pydantic import BaseModel, EmailStr
from app.models.enums import UserRole


class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: UserRole
    is_active: bool = True
    created_at: datetime

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: UserRole = UserRole.author


class UsersListOut(BaseModel):
    items: list[UserOut]
    total: int
    limit: int
    offset: int


class UserRoleUpdate(BaseModel):
    role: UserRole


class UserPasswordUpdate(BaseModel):
    password: str


class UserActiveUpdate(BaseModel):
    is_active: bool


class UserPasswordResetOut(BaseModel):
    temporary_password: str
