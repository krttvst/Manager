from fastapi import Depends, HTTPException, status, Request
import logging
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.deps import get_db
from app.models.user import User
from app.models.enums import UserRole

# OpenAPI "Authorize" flow must match the actual mounted route.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/login", auto_error=False)
logger = logging.getLogger("auth")


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    token: str | None = Depends(oauth2_scheme),
) -> User:
    if not token:
        cookie_token = request.cookies.get("access_token")
        token = cookie_token
    if not token:
        has_auth_header = bool(request.headers.get("authorization"))
        has_cookie = bool(request.cookies.get("access_token"))
        logger.warning(
            "Auth token missing. auth_header=%s cookie=%s path=%s",
            has_auth_header,
            has_cookie,
            request.url.path,
        )
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = jwt.decode(token, settings.app_secret, algorithms=["HS256"])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = db.get(User, int(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def require_roles(*roles: UserRole):
    def _checker(user: User = Depends(get_current_user)) -> User:
        if not roles:
            return user
        if user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return user

    return _checker


def require_api_key(request: Request) -> None:
    if not settings.n8n_api_key:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="API key not configured")
    api_key = request.headers.get("x-api-key")
    if api_key != settings.n8n_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
