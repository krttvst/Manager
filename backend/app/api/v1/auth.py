from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.schemas.auth import LoginRequest, TokenResponse
from app.services import auth as auth_service
from app.api.rate_limit import optional_rate_limiter

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/login",
    response_model=TokenResponse,
    dependencies=[Depends(optional_rate_limiter(times=5, seconds=60))],
)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    return auth_service.login(db, payload)
