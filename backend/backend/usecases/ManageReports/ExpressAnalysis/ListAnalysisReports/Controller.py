from fastapi import Depends, APIRouter
from pydantic import BaseModel
from datetime import datetime

from entities.repositories import Repository
from infrastructure.database import Database, get_db
from typing import List, Optional

from usecases.ManageUsers.AuthUser.guard import get_current_user_from_bearer
from utils.logging_config import setup_logging
import logging

setup_logging()
logger = logging.getLogger(__name__)

class ExpressAnalysisReportOut(BaseModel):
    id: int
    plant_id: int

    soil_humidity_mean: Optional[float] = None
    lumens_mean: Optional[float] = None
    air_humidity_mean: Optional[float] = None
    temperature_mean: Optional[float] = None

    soil_humidity_data: Optional[str] = None
    lumens_data: Optional[str] = None
    air_humidity_data: Optional[str] = None
    temperature_data: Optional[str] = None

    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True



router = APIRouter()
@router.get(
    "/reports/express-analysis",
    response_model=List[ExpressAnalysisReportOut]
)
def list_analysis_reports(db: Database = Depends(get_db), current = Depends(get_current_user_from_bearer)):
    repository = Repository(db)
    return [s.__dict__ for s in repository.list_all_express_reports(current.user_id)]
