from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from starlette import status

from entities.exceptions import NotFoundException, DatabaseConflictError, IllegalStateException
from entities.repositories import Repository
from infrastructure.database import Database, get_db
from usecases.ManageStations.PairStationToUser.PairStationToUserAction import PairStationToUserAction, \
    PairStationToUserParams
from usecases.ManageUsers.AuthUser.guard import get_current_user_from_bearer
import logging

from utils.deps import get_mqtt
from utils.mqtt_wrapper import MQTTWrapper

logger = logging.getLogger(__name__)

class PairingStationIn(BaseModel):
    pairing_code: str = Field(
        ...,
        min_length=1,
        max_length=12,
        description="code temportaire de jumelage",
        examples=["123456"]
    )

# Pour la documentation auto
class PairingStationOut(BaseModel):
    id: int
    name: str
    location: Optional[str] = None




router = APIRouter()

# @TODO PLM add response model response_model=PairingStationOut
@router.put("/stations-pairing", status_code=201)  # Route spécifique pour éviter conflit avec /stations/{station_id}
def pair_station_to_user(
    station_in: PairingStationIn,
    db: Database = Depends(get_db),
    mqtt:MQTTWrapper = Depends(get_mqtt),
    current_user = Depends(get_current_user_from_bearer)
):
    logger.info(f"Pairing request received: pairing_code={station_in.pairing_code}, user_id={current_user.user_id}")

    repo = Repository(db)
    try:
        params = PairStationToUserParams(
            user_id=current_user.user_id,
            pairing_code=station_in.pairing_code
        )
        PairStationToUserAction(mqtt, repo).execute(params)

        return {"status": "paired"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except NotFoundException as e:
        logger.info("%s: %s", type(e).__name__, e)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"the Station with id {station_in.pairing_code} cant be found"
        )
    except IllegalStateException as e:
        logger.info("%s: %s", type(e).__name__, e)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"pairing window expired for pairing code: {station_in.pairing_code}"
        )
    except DatabaseConflictError as e:
        logger.info("DatabaseConflictError:%s", e)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"The Station with {station_in.pairing_code} could not had been updated. Conflit or database constraint."
        )
    except Exception as e:
        logger.exception("Erreur interne: %s", e)
        raise HTTPException(status_code=500, detail="Erreur interne")

