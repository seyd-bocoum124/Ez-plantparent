from typing import Optional, Dict, Any
from pydantic import BaseModel, computed_field, field_validator, Field
import base64


class MaintenanceScheduleOut(BaseModel):
    plant_id: int
    plant_name: str
    watering_advices: Dict[str, Any]
    humidity_advices: Dict[str, Any]
    temperature_advices: Dict[str, Any]
    photo: Optional[bytes] = Field(default=None, exclude=True)
    
    @field_validator("photo", mode="before")
    @classmethod
    def convert_memoryview(cls, v):
        """Convertit memoryview en bytes si nécessaire"""
        if v is None:
            return None
        if isinstance(v, memoryview):
            return bytes(v)
        return v
    
    @computed_field
    @property
    def photo_base64(self) -> Optional[str]:
        """Convertit les bytes de la photo en base64 pour l'API"""
        if self.photo:
            return base64.b64encode(self.photo).decode('utf-8')
        return None
    
    class Config:
        from_attributes = True
