from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.api.deps import get_current_user, require_roles
from app.models.channel import Channel
from app.models.enums import UserRole
from app.schemas.channel import ChannelCreate, ChannelOut

router = APIRouter(prefix="/channels", tags=["channels"])


@router.get("/", response_model=list[ChannelOut])
def list_channels(db: Session = Depends(get_db), _user=Depends(get_current_user)):
    return db.query(Channel).all()


@router.post("/", response_model=ChannelOut)
def create_channel(
    payload: ChannelCreate,
    db: Session = Depends(get_db),
    _admin=Depends(require_roles(UserRole.admin)),
):
    existing = db.query(Channel).filter(Channel.telegram_channel_identifier == payload.telegram_channel_identifier).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Channel already exists")
    channel = Channel(title=payload.title, telegram_channel_identifier=payload.telegram_channel_identifier)
    db.add(channel)
    db.commit()
    db.refresh(channel)
    return channel


@router.get("/{channel_id}", response_model=ChannelOut)
def get_channel(channel_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user)):
    channel = db.get(Channel, channel_id)
    if not channel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")
    return channel
