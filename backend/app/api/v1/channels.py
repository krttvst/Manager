from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.api.deps import get_current_user, require_roles
from app.models.enums import UserRole
from app.schemas.channel import ChannelCreate, ChannelOut, ChannelLookupResponse
from app.usecases import channels as channel_usecase

router = APIRouter(prefix="/channels", tags=["channels"])


@router.get("", response_model=list[ChannelOut])
def list_channels(db: Session = Depends(get_db), _user=Depends(get_current_user)):
    return channel_usecase.list_channels(db)


@router.get("/lookup", response_model=ChannelLookupResponse)
def lookup_channel(identifier: str, db: Session = Depends(get_db), _user=Depends(get_current_user)):
    return channel_usecase.lookup_channel(db, identifier)


@router.post("", response_model=ChannelOut)
def create_channel(
    payload: ChannelCreate,
    db: Session = Depends(get_db),
    _admin=Depends(require_roles(UserRole.admin)),
):
    return channel_usecase.create_channel(db, payload)


@router.get("/{channel_id}", response_model=ChannelOut)
def get_channel(channel_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user)):
    return channel_usecase.get_channel(db, channel_id)


@router.delete("/{channel_id}", status_code=204)
def delete_channel(
    channel_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
    _admin=Depends(require_roles(UserRole.admin)),
):
    channel_usecase.delete_channel(db, channel_id, user)
