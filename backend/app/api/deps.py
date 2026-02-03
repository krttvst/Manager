from fastapi import Depends, HTTPException, status, Request
import logging
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.deps import get_db
from app.models.user import User
from app.models.enums import UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)
logger = logging.getLogger("auth")


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    token: str | None = Depends(oauth2_scheme),
) -> User:
    if not token:
        cookie_token = request.cookies.get("access_token")
        query_token = request.query_params.get("access_token")
        token = cookie_token or query_token
    if not token:
        has_auth_header = bool(request.headers.get("authorization"))
        has_cookie = bool(request.cookies.get("access_token"))
        has_query = bool(request.query_params.get("access_token"))
        logger.warning(
            "Auth token missing. auth_header=%s cookie=%s query=%s path=%s",
            has_auth_header,
            has_cookie,
            has_query,
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
        # Roles are currently not enforced (all users have full access).
        return user

    return _checker
