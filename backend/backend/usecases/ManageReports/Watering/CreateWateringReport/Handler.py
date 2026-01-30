from typing import Annotated, List, Optional
from pydantic import BaseModel, Field
import json


from entities.repositories import Repository
from infrastructure.database import Database

import logging

logger = logging.getLogger(__name__)

def remove_none(values):
    return [v for v in values if v is not None]

Percent = Annotated[float, Field(ge=0.0, le=100.0)]

ListPct = Annotated[List[Optional[Percent]], Field(min_items=0, max_items=600)]
ListPump = Annotated[List[Optional[Percent]], Field(min_items=0, max_items=600)]

class WateringReportPayload(BaseModel):
    plant_id: int = Field(..., ge=0, description="Identifiant de la plante")
    humidity: ListPct
    pump: ListPump
    sigma3: float = Field(..., ge=0.0, le=100.0, description="Écart-type (%)")
    mean: float = Field(..., ge=0.0, le=100.0, description="Moyenne (%)")
    target_humidity: float = Field(..., ge=0.0, le=100.0, description="Target humidity (%)")



def handle_watering_analysis(data: dict, db: Database):
    repo = Repository(db)
    try:
        payload = WateringReportPayload(**data)

        report_id = repo.create_watering_report(
            plant_id=payload.plant_id,
            soil_humidity_mean=payload.mean,
            soil_humidity_data=json.dumps(payload.humidity, separators=(",", ":")),
            pump_data=json.dumps(payload.pump, separators=(",", ":")),
            sigma3= payload.sigma3,
            target_humidity= payload.target_humidity,
        )

        logger.info(f"Report ID: {report_id}")
        return report_id
    except ValueError as e:
        logger.info("Erreur de validation: %s", e)
    except Exception as e:
        logger.info("Erreur: %s", e)
