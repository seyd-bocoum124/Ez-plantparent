import pytest
from starlette.testclient import TestClient

from entities.models import Station
from entities.repositories import Repository
from app import app
from infrastructure.database import get_db as get_db_dep
from usecases.ManageUsers.AuthUser.guard import get_current_user_from_bearer

@pytest.fixture(scope="function")
def client(tests_database):
    app.dependency_overrides[get_db_dep] = lambda: tests_database
    app.dependency_overrides[get_current_user_from_bearer] = lambda: {"id": 1, "email": "test@example.com"}

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.pop(get_db_dep, None)
    app.dependency_overrides.pop(get_current_user_from_bearer, None)

@pytest.fixture(scope="function")
def repo(tests_database) -> Repository:
    return Repository(tests_database)



class TestListStationsRoute:
    def test_when_no_stations_should_return_an_empty_list(self, client):
        # Act
        resp = client.get("/api/stations")

        # Assert
        assert resp.status_code == 200
        data = resp.json()

        assert isinstance(data, list)
        assert data == []

    def test_when_only_one_station_exist_should_return_in_a_list(self, client, repo: Repository):
        # Arrange
        station = Station(id=None, user_id=1, name="IntegrationStation", location="loc-x")
        station_id = repo.create_station(station)

        # Act
        resp = client.get("/api/stations")

        # Assert
        assert resp.status_code == 200
        data = resp.json()

        assert data == [{
            "id": station_id,
            "name": "IntegrationStation",
            "location":
                "loc-x"
        }]

    def test_when_two_stations_exist_should_return_in_a_list(self, client, repo: Repository):
        # Arrange
        station1 = Station(id=None, user_id=1, name="IntegrationStation", location="loc-x")
        station2 = Station(id=None, user_id=1, name="IntegrationBéta", location="a-second-location")
        station1_id = repo.create_station(station1)
        station2_id = repo.create_station(station2)


        # Act
        resp = client.get("/api/stations")

        # Assert
        assert resp.status_code == 200
        data = resp.json()

        assert data == [
                {
                "id": station1_id,
                "name": "IntegrationStation",
                "location": "loc-x"
            },
            {
                "id": station2_id,
                "name": "IntegrationBéta",
                "location": "a-second-location"
            }
        ]