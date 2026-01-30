import logging

from fastapi import Depends, APIRouter

from entities.repositories import Repository
from infrastructure.database import Database, get_db
from typing import List

from usecases.ManageStations.CreateStation.Controller import StationOut
from usecases.ManageUsers.AuthUser.guard import get_current_user_from_bearer
from utils.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

router = APIRouter()
@router.get("/stations", response_model=List[StationOut])
def list_stations(db: Database = Depends(get_db), current_user = Depends(get_current_user_from_bearer)):
    repository = Repository(db)
    return [s.__dict__ for s in repository.list_stations_by_user_id(current_user.user_id)]