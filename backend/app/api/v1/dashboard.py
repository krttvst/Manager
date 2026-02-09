from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.deps import get_db
from app.schemas.dashboard import DashboardOverview
from app.usecases import dashboard as dashboard_usecase

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/overview", response_model=DashboardOverview)
def overview(db: Session = Depends(get_db), _user=Depends(get_current_user)):
    return dashboard_usecase.get_overview(db)

