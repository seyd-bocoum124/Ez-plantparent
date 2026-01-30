from typing import Annotated, List, Optional
from pydantic import BaseModel, Field


from entities.repositories import Repository
from infrastructure.database import Database

import logging
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)

def remove_none(values):
    return [v for v in values if v is not None]

Percent = Annotated[float, Field(ge=0.0, le=100.0)]

ListPct = Annotated[List[Optional[Percent]], Field(min_items=0, max_items=600)]
ListPump = Annotated[List[Optional[Percent]], Field(min_items=0, max_items=600)]

class PairUserPayload(BaseModel):
    pairing_code: str = Field(
        ...,
        min_length=1,
        max_length=12,
        description="code temportaire de jumelage",
        examples=["Aurore"]
    ),
    station_id: str = Field(
        ...,
        min_length=12,
        max_length=12,
        description="Id de la station",
        examples=["Aurore"]
    )



def pair_station_to_user(data: dict, db: Database):
    repo = Repository(db)
    try:
        from entities.models import Station
        payload = PairUserPayload(**data)

        logger.info(f"Pairing request - Payload: {payload}")

        station = repo.get_station_by_mac_address(payload.station_id)
        pairing_timeout = datetime.now(timezone.utc) + timedelta(seconds=120)
        # TODO (PLM) check usecases when station is created not sure it exist
        if station:
            station.pairing_code = payload.pairing_code
            station.pairing_timeout = pairing_timeout

            repo.update_station(station)
            logger.info(f"Station updated with pairing code: {station.id}")
        else:
            new_station = Station(
                id=None,
                user_id=None,
                name=f"Station-{payload.station_id[-6:]}",
                location="Auto-paired",
                mac_adress=payload.station_id,
                pairing_code=payload.pairing_code,
                pairing_timeout=pairing_timeout
            )

            station_id = repo.create_station(new_station)
            logger.info(f"New station created with ID: {station_id}")
    except ValueError as e:
        logger.info("Erreur de validation: %s", e)
    except Exception as e:
        logger.info("Erreur: %s", e)
