from entities.repositories import Repository
from typing import Tuple
from datetime import datetime
from typing import Optional, TypeVar

import logging
logger = logging.getLogger(__name__)


def extract_last_felted(
    watering_date: Optional[datetime],
    watering_humidity: Optional[float],
    express_date: Optional[datetime],
    express_humidity: Optional[float]
) -> Tuple[Optional[datetime], Optional[float]]:
    """
    Détermine le rapport le plus récent entre watering et express analysis.
    Retourne (date, humidity) du plus récent, ou (None, None) si aucun n'existe.
    """
    if watering_date is not None and express_date is not None:
        # Les deux existent, prendre le plus récent
        if watering_date > express_date:
            return watering_date, watering_humidity
        else:
            return express_date, express_humidity
    elif watering_date is not None:
        # Seulement watering existe
        return watering_date, watering_humidity
    elif express_date is not None:
        # Seulement express existe
        return express_date, express_humidity
    else:
        # Aucun des deux
        return None, None


def calculate_days_since(date: Optional[datetime]) -> Optional[int]:
    """
    Calcule le nombre de jours depuis une date donnée jusqu'à aujourd'hui.
    Retourne None si la date est None.
    """
    if date is None:
        return None
    
    now = datetime.now(date.tzinfo) if date.tzinfo else datetime.now()
    delta = now - date
    return delta.days

def calculate_hours_since(date: Optional[datetime]) -> Optional[int]:
    """
    Calcule le nombre d'heures depuis une date donnée jusqu'à aujourd'hui.
    Retourne None si la date est None.
    """
    if date is None:
        return None
    
    now = datetime.now(date.tzinfo) if date.tzinfo else datetime.now()
    delta = now - date
    return int(delta.total_seconds() // 3600)




T = TypeVar("T")

def compare_values(v1: Optional[T], v2: Optional[T]) -> int:
    """
    Compare deux valeurs optionnelles de type ordonné.
    Retourne:
      -1 si v1 < v2
       0 si v1 == v2
       1 si v1 > v2
    Règle: None est considéré plus petit que toute valeur.
    """
    if v1 is None and v2 is None:
        return 0
    if v1 is None:
        return -1
    if v2 is None:
        return 1
    return (v1 > v2) - (v1 < v2)




class GetMaintenanceSchedulesAction:
    def __init__(self, repository: Repository):
        self._repository = repository

    def execute(self, user_id):
        mapped = []

        logger.info("Getting maintenance schedules for user %s", user_id)
        results = self._repository.get_last_feeled_humidity(user_id)

        for row in results:
            # Extraire le rapport le plus récent (watering vs express)
            last_felted_date, last_felted_humidity = extract_last_felted(
                row.last_watering_above_target_date,
                row.last_watering_above_target_humidity,
                row.last_express_above_target_date,
                row.last_express_above_target_humidity
            )

            last_test_date, last_test_humidity = extract_last_felted(
                row.last_watering_date,
                row.last_watering_humidity,
                row.last_express_date,
                row.last_express_soil_humidity
            )

            # Calculer les jours depuis les derniers rapports
            days_since_felted = calculate_days_since(last_felted_date)
            days_since_test = calculate_days_since(last_test_date)
            hours_since_test = calculate_hours_since(last_test_date)
            days_since_express = calculate_days_since(row.last_express_date)
            hours_since_express = calculate_hours_since(row.last_express_date)

            # target_air_humidity
            # last_express_air_humidity

            humidity_advices = {}
            if compare_values(row.min_air_humidity, row.last_express_air_humidity) > 0:
                humidity_advices = {
                    "status": "air_humidity_under_minimum",
                    "recommend_humidifier": True,
                }
            elif compare_values(row.target_air_humidity, row.last_express_air_humidity) > 0:
                humidity_advices = {
                    "status": "under_target_air_humidity",
                    "recommend_humidifier": True,
                }
            elif compare_values(row.max_air_humidity, row.last_express_air_humidity) < 0:
                humidity_advices = {
                    "status": "air_humidity_over_maximum",
                    "recommend_dehumidifier": True,
                }
            else:
                humidity_advices = {
                    "status": "air_humidity_ok",
                    "recommend_dehumidifier": False,
                }

            temperature_advices = {}
            if compare_values(row.min_temperature, row.last_express_temperature) > 0:
                temperature_advices = {
                    "status": "temperature_under_minimum",
                    "recommend_heater": True,
                }
            elif compare_values(row.target_temperature, row.last_express_temperature) > 0:
                temperature_advices = {
                    "status": "under_target_temperature",
                    "recommend_heater": True,
                }
            elif compare_values(row.max_temperature, row.last_express_temperature) < 0:
                temperature_advices = {
                    "status": "temperature_over_maximum",
                    "recommend_cooler": True,
                }
            else:
                temperature_advices = {
                    "status": "temperature_ok",
                    "recommend_adjustment": False,
                }

            watering_advices = {}
            if last_test_humidity is None:
                watering_advices = {
                    "status": "never_tested",
                    "require_emergency_analysis": True,
                }
            elif compare_values(row.min_soil_humidity, last_test_humidity) > 0:
                watering_advices = {
                    "status": "under_min_humidity",
                    "require_emergency_watering": True,
                    "days_under_min_humidity": days_since_test,
                    "day_before_watering": 0,
                }
            elif days_since_felted is None:
                watering_advices = {
                    "status": "never_felted",
                    "day_before_watering": 0,
                }
            elif days_since_felted > row.target_watering_days:
                watering_advices = {
                    "status": "watering_late",
                    "day_before_watering": row.target_watering_days - days_since_felted,
                    "last_felted_humidity": last_felted_humidity,
                    "days_since_felted": days_since_felted,
                }
            else:
                watering_advices = {
                    "status": "watering_ok",
                    "day_before_watering": row.target_watering_days - days_since_felted,
                    "last_felted_humidity": last_felted_humidity,
                    "days_since_felted": days_since_felted,
                }

            mapped.append({
                "plant_id": row.plant_id,
                "plant_name": row.plant_name,
                "photo": row.photo,
                "watering_advices": {
                    **watering_advices,
                    "details": {
                        "target_humidity": row.target_humidity,
                        "min_soil_humidity": row.min_soil_humidity,
                        "max_soil_humidity": row.max_soil_humidity,
                        "last_test_humidity": last_test_humidity,
                        "target_watering_days": row.target_watering_days,
                        "last_felted_humidity": last_felted_humidity,
                        "last_felted_date": last_felted_date,
                        "last_test_date": last_test_date,
                        "days_since_test": days_since_test,
                        "hours_since_test": hours_since_test,
                    }
                },
                "humidity_advices": {
                    **humidity_advices,
                        "details": {
                            "target_air_humidity": row.target_air_humidity,
                            "last_express_air_humidity": row.last_express_air_humidity,
                            "days_since_express": days_since_express,
                            "hours_since_express": hours_since_express,
                            "max_air_humidity": row.max_air_humidity,
                            "min_air_humidity": row.min_air_humidity,
                        }
                },
                "temperature_advices": {
                    **temperature_advices,
                        "details": {
                            "target_temperature": row.target_temperature,
                            "last_express_temperature": row.last_express_temperature,
                            "days_since_express": days_since_express,
                            "hours_since_express": hours_since_express,
                            "max_temperature": row.max_temperature,
                            "min_temperature": row.min_temperature,
                        }
                },
            })

        return mapped
