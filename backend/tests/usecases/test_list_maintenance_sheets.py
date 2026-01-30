import pytest
from starlette.testclient import TestClient
from entities.repositories import Repository
from app import app
from infrastructure.database import get_db as get_db_dep
from usecases.ManageUsers.AuthUser.guard import get_current_user_from_bearer, CurrentUser
import logging
from utils.logging_config import setup_logging
from entities.models import User, MaintenanceSheet

setup_logging()
logger = logging.getLogger(__name__)

@pytest.fixture(scope="function")
def repo(tests_database) -> Repository:
    return Repository(tests_database)

@pytest.fixture(scope="function")
def user(repo) -> User:
    return repo.get_or_create_user(email="test@example.com", google_sub="test")

@pytest.fixture(scope="function")
def client(tests_database, user):
    app.dependency_overrides[get_db_dep] = lambda: tests_database
    app.dependency_overrides[get_current_user_from_bearer] = lambda: CurrentUser(
        user_id=str(user.id),
        claims={
            "email": "test@example.com",
            "sub": "fake-sub-id",
            "roles": ["user", "admin"]
        }
    )


    with TestClient(app) as client:
        yield client

    app.dependency_overrides.pop(get_db_dep, None)
    app.dependency_overrides.pop(get_current_user_from_bearer, None)


class TestListMaintenanceSheets:

    def test_get_all_maintenance_sheets(self, client, repo: Repository, user: User):
        sheet = MaintenanceSheet(
            id = None,
            user_id=user.id,
            name="Fiche Monstera",
            scientific_name="Monstera Deliciosa",
            common_name="Plante gruyère",
            taxonkey=123,
            taxon_rank="species",
            gbif_id=456,
            identification_source="Other",
            confidence_score=90,
            min_soil_humidity=20,
            max_soil_humidity=60,
            min_lumens=1000,
            max_lumens=5000,
            lumens_unit="lux",
            min_air_humidity=40,
            max_air_humidity=80,
            min_temperature=18,
            max_temperature=28,
            min_watering_days_frequency=3,
            max_watering_days_frequency=7,
            created_at=None,
            updated_at=None,
        )

        sheet_id = repo.create_maintenance_sheet(sheet)

        resp = client.get("api/maintenance-sheets")

        assert resp.status_code == 200
        data = resp.json()

        assert data == [
            {
                "id": sheet_id,
                "user_id": user.id,
                "name": "Fiche Monstera",
                "scientific_name": "Monstera Deliciosa",
                "common_name": "Plante gruyère",
                "taxonkey": 123,
                "taxon_rank": "species",
                "gbif_id": 456,
                "identification_source": "Other",
                "confidence_score": 90,
                "min_soil_humidity": 20,
                "max_soil_humidity": 60,
                "min_lumens": 1000,
                "max_lumens": 5000,
                "lumens_unit": "lux",
                "min_air_humidity": 40,
                "max_air_humidity": 80,
                "min_temperature": 18,
                "max_temperature": 28,
                "min_watering_days_frequency": 3,
                "max_watering_days_frequency": 7,
                "created_at": sheet.created_at,
                "updated_at": sheet.updated_at
            }
 ]