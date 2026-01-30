from entities.models import MaintenanceSheet
from infrastructure.database import get_db

from entities.repositories import Repository

from typing import Optional, Union
from pydantic import BaseModel, Field, constr
from openai import OpenAI
import json
from datetime import datetime
from pydash import get
import logging
logger = logging.getLogger(__name__)
import os


CHAT_GPT_KEY = os.environ.get("CHAT_GPT_KEY")
if not CHAT_GPT_KEY or CHAT_GPT_KEY == "disabled":
    logger.warning("CHAT_GPT_KEY not set - AI features will be disabled")
    CHAT_GPT_KEY = None


ShortStr = constr(strip_whitespace=True, min_length=0, max_length=100)
MediumStr = constr(strip_whitespace=True, min_length=0, max_length=200)
LongStr = constr(strip_whitespace=True, min_length=0, max_length=500)


class CreateMaintenanceSheetParams(BaseModel):
    name: ShortStr = Field(..., title="Nom d'usage", example="Figuier d'intérieur")
    scientific_name: Optional[MediumStr] = Field(None, title="Nom scientifique", example="Ficus elastica")
    common_name: Optional[ShortStr] = Field(None, title="Nom commun", example="Caoutchouc")
    taxonkey: Optional[Union[int, ShortStr]] = Field(None, title="TaxonKey (int ou str)", example=123456)
    taxon_rank: Optional[ShortStr] = Field(None, title="Rang taxonomique (texte)", example="species")
    identification_source: Optional[ShortStr] = Field(None, title="Source d'identification", example="photo")
    gbif_id: Optional[int] = Field(None, title="gbif id", example=5304436)
    photo_base64: Optional[str] = Field(None, title="Photo en base64", example="data:image/jpeg;base64,...")

    class Config:
        anystr_strip_whitespace = True
        min_anystr_length = 0
        validate_assignment = True



def _build_chat_gpt_request_from_params(params: CreateMaintenanceSheetParams):
    request_text = {
        "name": params.name,
        "scientific_name": params.scientific_name,
        "common_name": params.common_name,
        "confidence_score_entier_pourcent": "xxxxxxx",
        "reccomanded_environement": {
            "relative_soil_humidity_in_percent": {"min": "xxxxxxx", "max": "xxxxxxx"},
            "lighting_in_lumens": {"min": "xxxxxxx", "max": "xxxxxxx"},
            "air_humidity_in_percent": {"min": "xxxxxxx", "max": "xxxxxxx"},
            "air_temperature_in_celcius": {"min": "xxxxxxx", "max": "xxxxxxx"},
            "watering_days_frequency": {"min": "xxxxxxx", "max": "xxxxxxx"}
        },
        "ideal_values": {
            "ideal_soil_humidity_after_watering_in_percent": "xxxxxxx",
            "ideal_air_humidity_in_percent": "xxxxxxx",
            "ideal_lumens": "xxxxxxx",
            "ideal_temperature_in_celcius": "xxxxxxx",
            "ideal_watering_days_frequency": "xxxxxxx"
        }
    }

    if params.identification_source == "PlantNet" :
        request_text["gbif_id"] = params.gbif_id
    else:
        request_text["taxonkey"] = params.taxonkey
        request_text["taxon_rank"] = params.taxon_rank

    json_str = json.dumps(request_text, ensure_ascii=False, indent=2)

    return "I only want the followed json file with the xxxxxxx values completed: " + json_str


def _decode_photo_base64(photo_base64: Optional[str]) -> Optional[bytes]:
    """Décode une photo base64 en bytes. Supporte le format data:image/jpeg;base64,... ou base64 pur."""
    if not photo_base64:
        return None
    
    import base64
    import re
    
    # Retirer le préfixe data:image/...;base64, si présent
    photo_base64 = re.sub(r'^data:image/[a-z]+;base64,', '', photo_base64)
    
    try:
        return base64.b64decode(photo_base64)
    except Exception as e:
        logger.warning(f"Failed to decode photo base64: {e}")
        return None


def _extract_maintenance_sheet(response, params):
    def _extract_response_text():
        texts = []
        for item in getattr(response, "output", []):
            if getattr(item, "type", None) == "message" and getattr(item, "role", None) == "assistant":
                for content in getattr(item, "content", []) or []:
                    if getattr(content, "type", "") == "output_text":
                        texts.append(getattr(content, "text", ""))
        return "\n\n".join(texts).strip()

    def _to_int(v):
        if v is None: return None
        try:
            return int(v)
        except (ValueError, TypeError):
            return None

    text = _extract_response_text()
    data = json.loads(text)
    now = datetime.utcnow()
    
    # Décoder la photo base64 en bytes
    photo_bytes = _decode_photo_base64(params.photo_base64)
    
    params = MaintenanceSheet(
        id=0,
        user_id=get(data, "user_id", 1),  # default 1 if absent
        name=params.name,
        scientific_name=params.scientific_name,
        common_name=params.common_name,
        taxonkey=params.taxonkey,
        taxon_rank=params.taxon_rank,
        gbif_id=params.gbif_id,
        identification_source=params.identification_source,
        confidence_score=_to_int(get(data, "confidence_score_entier_pourcent")),
        min_soil_humidity=_to_int(get(data, "reccomanded_environement.relative_soil_humidity_in_percent.min")),
        max_soil_humidity=_to_int(get(data, "reccomanded_environement.relative_soil_humidity_in_percent.max")),
        min_lumens=_to_int(get(data, "reccomanded_environement.lighting_in_lumens.min")),
        max_lumens=_to_int(get(data, "reccomanded_environement.lighting_in_lumens.max")),
        lumens_unit=get(data, "lumens_unit", "lumens"),
        min_air_humidity=_to_int(get(data, "reccomanded_environement.air_humidity_in_percent.min")),
        max_air_humidity=_to_int(get(data, "reccomanded_environement.air_humidity_in_percent.max")),
        min_temperature=_to_int(get(data, "reccomanded_environement.air_temperature_in_celcius.min")),
        max_temperature=_to_int(get(data, "reccomanded_environement.air_temperature_in_celcius.max")),
        min_watering_days_frequency=_to_int(get(data, "reccomanded_environement.watering_days_frequency.min")),
        max_watering_days_frequency=_to_int(get(data, "reccomanded_environement.watering_days_frequency.max")),
        ideal_soil_humidity_after_watering=_to_int(get(data, "ideal_values.ideal_soil_humidity_after_watering_in_percent")),
        ideal_air_humidity=_to_int(get(data, "ideal_values.ideal_air_humidity_in_percent")),
        ideal_lumens=_to_int(get(data, "ideal_values.ideal_lumens")),
        ideal_temperature=_to_int(get(data, "ideal_values.ideal_temperature_in_celcius")),
        ideal_watering_days_frequency=_to_int(get(data, "ideal_values.ideal_watering_days_frequency")),
        photo=photo_bytes,
        created_at=now,
        updated_at=now,
    )
    return params



class CreateMaintenanceSheetAction:
    def __init__(self, repo:Repository):
        if repo is None:
            db = get_db()
            self.repo = Repository(db)
        else:
            self.repo = repo


    def execute(self, params: CreateMaintenanceSheetParams, user_id):
        logger.info("Creating maintenance sheet for user %s", user_id)
        
        if not CHAT_GPT_KEY:
            logger.error("Cannot create maintenance sheet: CHAT_GPT_KEY not configured")
            raise RuntimeError("AI features are disabled. CHAT_GPT_KEY must be configured.")
        
        client = OpenAI(api_key=CHAT_GPT_KEY)
        response = client.responses.create(
            model="gpt-5-nano",
            input=_build_chat_gpt_request_from_params(params),
            store=True, ## XXXXX vérifier
        )

        maintenance_sheet_params = _extract_maintenance_sheet(response, params)
        maintenance_sheet_params.user_id = user_id
        maintenance_sheet_id = self.repo.create_maintenance_sheet(maintenance_sheet_params)

        return self.repo.get_maintenance_sheet_by_id(maintenance_sheet_id)







