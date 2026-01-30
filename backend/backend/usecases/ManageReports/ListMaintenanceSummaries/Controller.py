from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime

from entities.exceptions import IllegalArgumentException
from entities.repositories import Repository
from infrastructure.database import Database, get_db
from typing import List, Optional

from usecases.ManageReports.ListMaintenanceSummaries.ListMaintenanceSummariesAction import \
    ListMaintenanceSummariesAction, ListMaintenanceSummariesParams

from usecases.ManageUsers.AuthUser.guard import get_current_user_from_bearer
from utils.logging_config import setup_logging
import logging

setup_logging()
logger = logging.getLogger(__name__)

class MaintenanceSummaryOut(BaseModel):
    id: int
    plant_id: int
    type: str  # 'express' ou 'watering'

    soil_humidity_mean: Optional[float] = None
    lumens_mean: Optional[float] = None
    air_humidity_mean: Optional[float] = None
    temperature_mean: Optional[float] = None

    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True



router = APIRouter()
@router.get(
    "/plants/{plant_id}/reports/resumes",
    response_model=List[MaintenanceSummaryOut]

)
def list_plant_reports_resumes(plant_id: int, db: Database = Depends(get_db), current = Depends(get_current_user_from_bearer)):
    repository = Repository(db)
    try:
        params = ListMaintenanceSummariesParams(sheet_id=plant_id, user_id=current.user_id)
        return ListMaintenanceSummariesAction(repository).execute(params)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except IllegalArgumentException:
        raise HTTPException(
            status_code=401,
            detail=f"Unauthorized"
        )
    except Exception:
        raise HTTPException(
            status_code=401,
            detail=f"Unauthorized"
        )
