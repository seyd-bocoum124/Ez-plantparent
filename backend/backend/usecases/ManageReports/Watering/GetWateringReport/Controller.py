from fastapi import HTTPException

from fastapi import APIRouter, Depends

from entities.exceptions import NotFoundException, UnauthorizedError
from entities.repositories import Repository
from infrastructure.database import Database, get_db
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from usecases.ManageReports.Watering.GetWateringReport.GetWateringReportAction import GetWateringReportAction
from usecases.ManageUsers.AuthUser.guard import get_current_user_from_bearer

router = APIRouter()

import logging
logger = logging.getLogger(__name__)


class WateringReportOut(BaseModel):
    id: int
    plant_id: int

    soil_humidity_mean: Optional[float] = None
    sigma3: Optional[float] = None
    target_humidity: Optional[float] = None

    soil_humidity_data: Optional[str] = None
    pump_data: Optional[str] = None

    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True



@router.get("/reports/watering/{report_id}",
            response_model=WateringReportOut
            )
def get_watering_report(report_id: int, db: Database = Depends(get_db), current = Depends(get_current_user_from_bearer)):
    repository = Repository(db)
    try:
        return GetWateringReportAction(repository).execute(report_id, current.user_id)
    except (NotFoundException, UnauthorizedError) as e:
        raise HTTPException(status_code=404, detail=e.message)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500,
                            detail="Une erreure interne s'est produite!")