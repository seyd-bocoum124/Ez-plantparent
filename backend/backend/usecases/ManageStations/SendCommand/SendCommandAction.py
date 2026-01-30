from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict
import logging

from entities.repositories import Repository
from usecases.ManageFicheEntretien.GetMaintenanceSheet.GetMaintenanceSheetAction import GetMaintenanceSheetByIdAction, \
    GetMaintenanceSheetParams
from utils.mqtt_wrapper import MQTTWrapper
from entities.exceptions import NotFoundException, IllegalArgumentException

logger = logging.getLogger(__name__)

class CommandType(str, Enum):
    send_all_data = "send_all_data"
    express_analysis = "express_analysis"
    watering = "watering"

class CommandActions(str, Enum):
    start = 'start'
    stop = 'stop'

class SendCommandParams(BaseModel):
    type: CommandType
    action: CommandActions
    station_id: str
    duration: Optional[int] = None
    plant_id: int
    user_id: int

    model_config = ConfigDict(
        extra="forbid"
    )



class SendCommandAction:
    def __init__(self, mqtt:MQTTWrapper, repository: Repository):
        self.queue = mqtt
        self._repository = repository


    def execute(self, params: SendCommandParams):
        self._check_station_belong_to_user(params)

        payload = {
            "type": "command",
            "activity": params.type,
            "action": params.action,
            "plant_id": params.plant_id,
        }

        if params.duration is not None:
            payload["duration"] = params.duration

        # @TODO (PLM) add error management at the top level
        plant = GetMaintenanceSheetByIdAction(self._repository).execute(
            GetMaintenanceSheetParams(
                sheet_id=params.plant_id,
                user_id=params.user_id
            )
        )

        payload["data"] = {
            "max_soil_humidity": plant.max_soil_humidity,
            "min_soil_humidity": plant.min_soil_humidity,
            "ideal_soil_humidity_after_watering": plant.ideal_soil_humidity_after_watering,
        }

        # @TODO (PLM) extract from db when pairing will be (dont need in params and bettetr access control)
        self.queue.publish_json(f"stations/{params.station_id}", payload)

        return {
            "message": "Command sent successfully",
        }

    def _check_station_belong_to_user(self, params):
        station = self._repository.get_station_by_mac_address(params.station_id)
        if station is None or station.user_id != params.user_id:
            # reduce enumeration attack risks
            raise NotFoundException(f"Station with id {params.station_id} not found")
