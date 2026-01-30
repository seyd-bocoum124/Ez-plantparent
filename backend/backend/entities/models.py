from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Any


@dataclass
class Station:
    id: int | None
    user_id: int | None
    name: str
    location: str | None
    created_at: datetime | None = None
    pairing_code: str | None = None
    mac_adress: str | None = None
    pairing_timeout: datetime | None = None

@dataclass
class Capteur:
    id: int | None
    station_id: int
    type: str
    unit: str | None
    created_at: datetime | None = None

@dataclass
class Intervention:
    id: int | None
    station_id: int
    description: str
    performed_at: datetime | None = None

@dataclass
class MaintenanceSheet:
    id: int
    user_id: int
    name: str
    scientific_name: str
    common_name: Optional[str]
    taxonkey: Optional[int]
    taxon_rank: Optional[str]
    gbif_id: Optional[int]
    identification_source: str
    confidence_score: Optional[int]
    min_soil_humidity: Optional[int]
    max_soil_humidity: Optional[int]
    min_lumens: Optional[int]
    max_lumens: Optional[int]
    lumens_unit: Optional[str]
    min_air_humidity: Optional[int]
    max_air_humidity: Optional[int]
    min_temperature: Optional[int]
    max_temperature: Optional[int]
    min_watering_days_frequency: Optional[int]
    max_watering_days_frequency: Optional[int]
    ideal_soil_humidity_after_watering: Optional[int]
    ideal_air_humidity: Optional[int]
    ideal_lumens: Optional[int]
    ideal_temperature: Optional[int]
    ideal_watering_days_frequency: Optional[int]
    photo: Optional[bytes]
    created_at: Optional[Any]
    updated_at: Optional[Any]


@dataclass
class ExpressAnalysisReport:
    id: int
    plant_id: int
    analysis_type: str  # 'express' ou 'watering'

    soil_humidity_mean: Optional[float] = None
    lumens_mean: Optional[float] = None
    air_humidity_mean: Optional[float] = None
    temperature_mean: Optional[float] = None

    soil_humidity_data: Optional[str] = None
    lumens_data: Optional[str] = None
    air_humidity_data: Optional[str] = None
    temperature_data: Optional[str] = None

    created_at: Optional[datetime] = None

@dataclass
class WateringReport:
    id: int
    plant_id: int

    soil_humidity_mean: Optional[float] = None
    sigma3: Optional[float] = None
    target_humidity: Optional[float] = None

    soil_humidity_data: Optional[str] = None
    pump_data: Optional[str] = None

    created_at: Optional[datetime] = None

@dataclass
class MaintenanceSummary:
    id: int
    plant_id: int
    created_at: datetime
    type: str

    soil_humidity_mean: Optional[float] = None
    lumens_mean: Optional[float] = None
    air_humidity_mean: Optional[float] = None
    temperature_mean: Optional[float] = None


@dataclass
class LastFeeledHumidity:
    plant_id: int
    plant_name: str
    
    # Soil humidity targets
    ideal_soil_humidity_after_watering: Optional[int]
    min_soil_humidity: Optional[int]
    max_soil_humidity: Optional[int]
    target_humidity: float  # Calculé: ideal ou moyenne min/max
    
    # Air humidity targets
    ideal_air_humidity: Optional[int]
    min_air_humidity: Optional[int]
    max_air_humidity: Optional[int]
    target_air_humidity: float  # Calculé: ideal ou moyenne min/max
    
    # Temperature targets
    ideal_temperature: Optional[int]
    min_temperature: Optional[int]
    max_temperature: Optional[int]
    target_temperature: float  # Calculé: ideal ou moyenne min/max
    
    # Watering frequency targets
    ideal_watering_days_frequency: Optional[int]
    min_watering_days_frequency: Optional[int]
    max_watering_days_frequency: Optional[int]
    target_watering_days: float  # Calculé: ideal ou moyenne min/max
    
    # Last reports with humidity > target
    last_watering_above_target_id: Optional[int] = None
    last_watering_above_target_date: Optional[datetime] = None
    last_watering_above_target_humidity: Optional[float] = None
    
    last_express_above_target_id: Optional[int] = None
    last_express_above_target_date: Optional[datetime] = None
    last_express_above_target_humidity: Optional[float] = None
    
    # Last reports (unconditional)
    last_watering_id: Optional[int] = None
    last_watering_date: Optional[datetime] = None
    last_watering_humidity: Optional[float] = None
    
    last_express_id: Optional[int] = None
    last_express_date: Optional[datetime] = None
    last_express_soil_humidity: Optional[float] = None
    last_express_air_humidity: Optional[float] = None
    last_express_temperature: Optional[float] = None
    
    photo: Optional[bytes] = None


@dataclass
class RefreshToken:
    id: Optional[int]
    user_id: str
    email: str
    expires_at: datetime
    revoked: bool = False

@dataclass
class User:
    id: Optional[int]
    google_sub: str
    email: str
    created_at: Optional[datetime] = None



