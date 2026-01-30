from entities.models import Station
from entities.exceptions import NotFoundException, DatabaseConflictError, IllegalStateException
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import logging
from entities.repositories import Repository
from utils.logging_config import setup_logging
from utils.mqtt_wrapper import MQTTWrapper

setup_logging()
logger = logging.getLogger(__name__)


class PairStationToUserParams(BaseModel):
    user_id: int = Field(
        ...,
        description="L'ID de l'utilisateur propriétaire"
    )
    pairing_code: str = Field(
        ...,
        min_length=1,
        max_length=12,
        description="code temportaire de jumelage",
        examples=["Aurore"]
    )


class PairStationToUserAction:
    def __init__(self, mqtt:MQTTWrapper, repository: Repository):
        self.queue = mqtt
        self.repo = repository


    def execute(self, params: PairStationToUserParams):
        logger.info(f"Pairing station to user with params: {params}")
        station = self._try_get_station_by_pairing_code(params.pairing_code)

        _check_station_pairing_window(station)

        station.user_id = params.user_id
        station.pairing_timeout = None

        self._try_update_station(station)

        self._try_delete_other_user_stations(params.user_id, station.id)

        payload = {
            "type": "command",
            "activity": "pair_user",
            "action": "confirm_pair"
        }

        self.queue.publish_json(f"stations/{station.mac_adress}", payload)

    def _try_get_station_by_pairing_code(self, pairing_code:str) -> Station:
        maintenance_sheet = self.repo.get_station_by_pairing_code(pairing_code)
        if not maintenance_sheet:
            raise NotFoundException(f"Station with pairing code: {pairing_code} not found.")
        return maintenance_sheet

    def _try_update_station(self, station):
        result = self.repo.update_station(station)
        if not result:
            raise DatabaseConflictError(
                f"Update of Station with id: {station.id} encounter database conflict.")

    def _try_delete_other_user_stations(self, user_id: int, keep_station_id: int):
        deleted_count = self.repo.delete_other_user_stations(user_id, keep_station_id)
        logger.info(f"Deleted {deleted_count} other station(s) for user {user_id}")



def _check_station_pairing_window(station:Station):
    if station.pairing_timeout is None:
        raise IllegalStateException(f"No pairing timeout set for code: {station.pairing_code}")

    if station.pairing_timeout < datetime.now(timezone.utc):
        raise IllegalStateException(f"Pairing window expired for code: {station.pairing_code}")