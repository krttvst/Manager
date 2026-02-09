from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.db.deps import get_db
from app.models.enums import UserRole
from app.schemas.inbox import SuggestionInboxOut
from app.usecases import inbox as inbox_usecase

router = APIRouter(prefix="/inbox", tags=["inbox"])


@router.get("/suggestions", response_model=SuggestionInboxOut)
def suggestions_inbox(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    channel_id: int | None = None,
    q: str | None = None,
    db: Session = Depends(get_db),
    _editor=Depends(require_roles(UserRole.editor, UserRole.admin)),
):
    return inbox_usecase.list_suggestions_inbox(db, limit=limit, offset=offset, channel_id=channel_id, q=q)

