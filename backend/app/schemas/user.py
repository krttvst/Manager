from datetime import datetime
from pydantic import BaseModel, EmailStr
from app.models.enums import UserRole


class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: UserRole
    created_at: datetime

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: UserRole = UserRole.author
