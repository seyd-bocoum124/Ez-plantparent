from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from entities.repositories import Repository
from infrastructure.database import Database, get_db
from usecases.ManageStations.CreateStation.CreateStationAction import (
    CreateStationParams,
    CreateStationAction
)
from usecases.ManageUsers.AuthUser.guard import get_current_user_from_bearer
import logging
logger = logging.getLogger(__name__)

class StationIn(BaseModel):
    name: str
    location: str

# Pour la documentation auto
class StationOut(BaseModel):
    id: int
    name: Optional[str] = None
    location: Optional[str] = None
    mac_adress: Optional[str] = None




router = APIRouter()

@router.post("/stations", response_model=StationOut, status_code=201)
def create_station(
    station_in: StationIn,
    db: Database = Depends(get_db),
    current_user = Depends(get_current_user_from_bearer)
):
    repo = Repository(db)
    try:
        params = CreateStationParams(
            user_id=current_user.user_id,
            name=station_in.name,
            location=station_in.location
        )
        station = CreateStationAction(repo).execute(params)
        return StationOut(
            id=station.id,
            name=station.name,
            location=station.location
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Erreur interne: %s", e)
        raise HTTPException(status_code=500, detail="Erreur interne")

