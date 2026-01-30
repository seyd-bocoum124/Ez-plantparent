from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator, conint, computed_field
from datetime import datetime
import base64

# types contraints
Percent = conint(ge=0, le=100)
TempC = conint(ge=-50, le=60)
NonNegInt = conint(ge=0)

IDENTIFICATION_CHOICES = ('GBIF', 'PlantNet', 'Other')

class MaintenanceSheet(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: int
    name: str
    scientific_name: str
    common_name: Optional[str] = None
    taxonkey: Optional[int] = None
    taxon_rank: Optional[str] = None
    gbif_id: Optional[int] = None
    identification_source: str = Field(default='Other')
    confidence_score: Optional[Percent] = None

    min_soil_humidity: Optional[Percent] = None
    max_soil_humidity: Optional[Percent] = None

    min_lumens: Optional[NonNegInt] = None
    max_lumens: Optional[NonNegInt] = None
    lumens_unit: str = Field(default='lux')

    min_air_humidity: Optional[Percent] = None
    max_air_humidity: Optional[Percent] = None

    min_temperature: Optional[TempC] = None
    max_temperature: Optional[TempC] = None

    min_watering_days_frequency: Optional[NonNegInt] = None
    max_watering_days_frequency: Optional[NonNegInt] = None
    
    ideal_soil_humidity_after_watering: Optional[Percent] = None
    ideal_air_humidity: Optional[Percent] = None
    ideal_lumens: Optional[NonNegInt] = None
    ideal_temperature: Optional[TempC] = None
    ideal_watering_days_frequency: Optional[NonNegInt] = None
    
    photo: Optional[bytes] = Field(default=None, exclude=True)

    @field_validator("photo", mode="before")
    @classmethod
    def convert_memoryview_to_bytes(cls, v):
        """Convertit memoryview (retourné par PostgreSQL) en bytes"""
        if v is None:
            return None
        if isinstance(v, memoryview):
            return bytes(v)
        return v

    @field_validator("identification_source")
    @classmethod
    def check_identification_source(cls, v: str) -> str:
        if v not in IDENTIFICATION_CHOICES:
            raise ValueError(f"identification_source must be one of {IDENTIFICATION_CHOICES}")
        return v

    @field_validator("max_soil_humidity", mode="after")
    @classmethod
    def check_soil_humidity(cls, v, info):
        mn = info.data.get("min_soil_humidity")
        if mn is not None and v is not None and mn > v:
            raise ValueError("min_soil_humidity must be <= max_soil_humidity")
        return v

    @field_validator("max_lumens", mode="after")
    @classmethod
    def check_lumens(cls, v, info):
        mn = info.data.get("min_lumens")
        if mn is not None and v is not None and mn > v:
            raise ValueError("min_lumens must be <= max_lumens")
        return v

    @field_validator("max_air_humidity", mode="after")
    @classmethod
    def check_air_humidity(cls, v, info):
        mn = info.data.get("min_air_humidity")
        if mn is not None and v is not None and mn > v:
            raise ValueError("min_air_humidity must be <= max_air_humidity")
        return v

    @field_validator("max_temperature", mode="after")
    @classmethod
    def check_temperature(cls, v, info):
        mn = info.data.get("min_temperature")
        if mn is not None and v is not None and mn > v:
            raise ValueError("min_temperature must be <= max_temperature")
        return v

class MaintenanceSheetOut(MaintenanceSheet):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @computed_field
    @property
    def photo_base64(self) -> Optional[str]:
        """Convertit les bytes de la photo en base64 pour l'API"""
        if self.photo:
            return base64.b64encode(self.photo).decode('utf-8')
        return None
