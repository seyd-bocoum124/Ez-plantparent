import pytest
from entities.repositories import Repository
from usecases.ManageFicheEntretien.CreateMaintenanceSheet.CreateByName.CreateMaintenanceSheetAction import (
    CreateMaintenanceSheetAction,
    CreateMaintenanceSheetParams
)
from openai.resources.responses import Responses
import json

@pytest.fixture(scope="function")
def repo(tests_database) -> Repository:
    return Repository(tests_database)


class FakeContent:
    def __init__(self, user_id: int = 42):
        self.type = "output_text"
        payload = {
            "user_id": user_id,
            "confidence_score_entier_pourcent": 90,
            "reccomanded_environement": {
                "relative_soil_humidity_in_percent": {"min": 10, "max": 20},
                "lighting_in_lumens": {"min": 1000, "max": 2000},
                "air_humidity_in_percent": {"min": 40, "max": 80},
                "air_temperature_in_celcius": {"min": 18, "max": 28},
                "watering_days_frequency": {"min": 3, "max": 7},
            },
            "lumens_unit": "lux"
        }
        self.text = json.dumps(payload)

class FakeMessage:
    def __init__(self, user_id: int = 42):
        self.type = "message"
        self.role = "assistant"
        self.content = [FakeContent(user_id)]

class FakeResponse:
    def __init__(self, user_id: int = 42):
        self.output = [FakeMessage(user_id)]



class TestCreateMaintenanceSheetAction:

    def test_should_create_and_return_sheet(self, repo, monkeypatch):
        # Arrange
        user = repo.get_or_create_user(email="an-email", google_sub="a-google-sub")

        params = CreateMaintenanceSheetParams(
            name="Aloe Vera",
            scientific_name="Aloe barbadensis",
            common_name="Aloès",
            taxonkey=123,
            taxon_rank="species",
            identification_source="PlantNet"
        )

        action = CreateMaintenanceSheetAction(repo)

        monkeypatch.setattr(
            Responses,
            "create",
            lambda self, model, input, store: FakeResponse(user_id=user.id)
        )

        # Act
        sheet = action.execute(params, user_id=user.id)

        # Assert
        assert sheet is not None
        assert sheet.user_id == user.id
        assert sheet.name == "Aloe Vera"
        assert sheet.scientific_name == "Aloe barbadensis"
        assert sheet.confidence_score == 90

        assert sheet.min_soil_humidity == 10
        assert sheet.max_soil_humidity == 20
        assert sheet.min_lumens == 1000
        assert sheet.max_lumens == 2000

        saved = repo.get_maintenance_sheet_by_id(sheet.id)
        assert saved is not None
        assert saved.id == sheet.id
