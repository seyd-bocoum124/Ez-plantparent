from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
import logging

from starlette import status

from entities.exceptions import NotFoundException
from entities.repositories import Repository
from infrastructure.database import Database, get_db
from usecases.ManageStations.SendCommand.SendCommandAction import SendCommandAction, CommandType, \
    CommandActions, SendCommandParams
from usecases.ManageUsers.AuthUser.guard import get_current_user_from_bearer
from utils.deps import get_mqtt
from utils.mqtt_wrapper import MQTTWrapper

logger = logging.getLogger(__name__)

class CommandOut(BaseModel):
    message: str


class SendCommandIn(BaseModel):
    type: CommandType
    action: CommandActions
    plant_id: int
    duration: Optional[int] = Field(default=None, le=120)


router = APIRouter()

@router.post("/stations/{station_id}/command", response_model=CommandOut, status_code=201)
def create_station(
        station_id: str,
        params_in: SendCommandIn,
        mqtt:MQTTWrapper = Depends(get_mqtt),
        current = Depends(get_current_user_from_bearer),
        db: Database = Depends(get_db)
    ):
    try:
        repository = Repository(db)
        params = SendCommandParams(**params_in.model_dump(), station_id=station_id, user_id=current.user_id)

        result = SendCommandAction(mqtt, repository).execute(params)

        return CommandOut(
            message=result.get('message')
        )
    except NotFoundException as e:
        logger.info("%s: %s", type(e).__name__, e)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"the station cannot be found"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Erreur interne: %s", e)
        raise HTTPException(status_code=500, detail="Erreur interne")

