from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.api.deps import get_current_user, require_api_key, require_roles
from app.api.rate_limit import optional_rate_limiter
from app.models.enums import UserRole
from app.schemas.suggestion import SuggestionCreate, SuggestionOut
from app.schemas.post import PostOut
from app.usecases import suggestions as suggestion_usecase

router = APIRouter(prefix="/channels/{channel_id}/suggestions", tags=["suggestions"])


@router.post(
    "",
    response_model=SuggestionOut,
    dependencies=[Depends(require_api_key), Depends(optional_rate_limiter(times=30, seconds=60))],
)
def create_suggestion(
    channel_id: int,
    payload: SuggestionCreate,
    db: Session = Depends(get_db),
):
    return suggestion_usecase.create_suggestion(db, channel_id, payload)


@router.get("", response_model=list[SuggestionOut])
def list_suggestions(
    channel_id: int,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    return suggestion_usecase.list_suggestions(db, channel_id, limit=limit, offset=offset)


@router.post("/{suggestion_id}/accept", response_model=PostOut)
def accept_suggestion(
    channel_id: int,
    suggestion_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
    _editor=Depends(require_roles(UserRole.editor, UserRole.admin)),
):
    return suggestion_usecase.accept_suggestion(db, channel_id, suggestion_id, user)


@router.delete("/{suggestion_id}", status_code=204)
def reject_suggestion(
    channel_id: int,
    suggestion_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
    _editor=Depends(require_roles(UserRole.editor, UserRole.admin)),
):
    suggestion_usecase.reject_suggestion(db, channel_id, suggestion_id, user)
