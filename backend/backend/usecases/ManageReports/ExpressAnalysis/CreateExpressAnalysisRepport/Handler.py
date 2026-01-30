from typing import Annotated, List, Optional
from pydantic import BaseModel, Field
import statistics
import json


from entities.repositories import Repository
from infrastructure.database import Database

import logging
logger = logging.getLogger(__name__)


Percent = Annotated[float, Field(ge=0.0, le=100.0)]
Temp = Annotated[float, Field(ge=-100.0, le=200.0)]

ListPct = Annotated[List[Optional[Percent]], Field(min_items=0, max_items=60)]
ListTemp = Annotated[List[Optional[Temp]], Field(min_items=0, max_items=60)]
ListFloat = Annotated[List[Optional[float]], Field(min_items=0, max_items=60)]


class ExpressAnalysisPayload(BaseModel):
    plant_id: int = Field(..., ge=0, description="Identifiant de la plante")
    humidity: ListPct
    temperature: ListTemp
    air_humidity: ListFloat

def remove_none(values):
    return [v for v in values if v is not None]

def handle_express_analysis(data: dict, db: Database):
    repo = Repository(db)
    try:
        payload = ExpressAnalysisPayload(**data)

        soil = payload.humidity
        temp = payload.temperature
        air = payload.air_humidity

        soil_vals = remove_none(soil)
        temp_vals = remove_none(temp)
        air_vals = remove_none(air)

        soil_mean = statistics.mean(soil_vals) if soil_vals else None
        temp_mean = statistics.mean(temp_vals) if temp_vals else None
        air_mean = statistics.mean(air_vals) if air_vals else None

        soil_json = json.dumps(soil, separators=(",", ":"))
        temp_json = json.dumps(temp, separators=(",", ":"))
        air_json = json.dumps(air, separators=(",", ":"))

        report_id = repo.create_express_analysis_report(
            plant_id=payload.plant_id,
            soil_humidity_mean=soil_mean,
            temperature_mean=temp_mean,
            air_humidity_mean=air_mean,
            lumens_mean=None,
            soil_humidity_data=soil_json,
            temperature_data=temp_json,
            air_humidity_data=air_json,
            lumens_data=None,
        )

        logger.info(f"Report ID: {report_id}")
        return report_id
    except ValueError as e:
        logger.info("Erreur de validation: %s", e)
    except Exception as e:
        logger.info("Erreur: %s", e)
