import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from infrastructure.database import get_db as get_db_dependency
from entities.models import Station

import usecases.ManageStations.UpdateStation.Controller as controller_module


@pytest.fixture(scope="function")
def app():
    """
    App FastAPI éphémère avec le router du controller.
    """
    app = FastAPI()
    app.include_router(controller_module.router)
    return app


@pytest.fixture(scope="function")
def client(app: FastAPI):
    return TestClient(app)


@pytest.fixture(scope="function")
def fake_db():
    """
    Faux objet DB juste pour satisfaire Repository(db).
    """
    return object()


@pytest.fixture(scope="function")
def override_dependencies(app: FastAPI, fake_db):
    """
    Override de la dépendance get_db utilisée dans le controller.
    On override la fonction importée depuis infrastructure.database.
    """
    def _fake_get_db():
        return fake_db

    app.dependency_overrides[get_db_dependency] = _fake_get_db
    yield
    app.dependency_overrides.clear()


class TestUpdateStationController:
    class TestWhenUpdateOk:
        def test_returns_200_and_calls_repository_with_correct_station(
            self,
            client: TestClient,
            override_dependencies,
            fake_db,
            monkeypatch,
        ):
            # Arrange
            created = {}

            class FakeRepository:
                def __init__(self, db):
                    # On vérifie qu'on reçoit bien le fake_db
                    assert db is fake_db
                    created["db"] = db

                def update_station(self, station):
                    # On capture la station passée
                    created["station"] = station

            # On remplace Repository par notre fake dans le module du controller
            monkeypatch.setattr(
                controller_module,
                "Repository",
                FakeRepository,
            )

            station_id = 42
            payload = {
                "name": "Station Test",
                "location": "Paris",
            }

            # Act
            response = client.put(f"/stations/{station_id}", json=payload)

            # Assert
            assert response.status_code == 200
            body = response.json()
            assert body == {"status": "updated"}

            # On vérifie que le repo a été instancié
            assert "db" in created
            assert "station" in created

            # On vérifie que update_station a reçu une Station correctement construite
            station = created["station"]
            assert isinstance(station, Station)
            assert station.id == station_id
            assert station.name == payload["name"]
            assert station.location == payload["location"]
            # Le controller ne passe pas created_at : il doit rester à None
            assert station.created_at is None

    class TestWhenLocationIsOptional:
        def test_can_update_without_location(
            self,
            client: TestClient,
            override_dependencies,
            fake_db,
            monkeypatch,
        ):
            created = {}

            class FakeRepository:
                def __init__(self, db):
                    created["db"] = db

                def update_station(self, station):
                    created["station"] = station

            monkeypatch.setattr(
                controller_module,
                "Repository",
                FakeRepository,
            )

            station_id = 7
            payload = {
                "name": "Sans Lieu",
                # pas de "location"
            }

            # Act
            response = client.put(f"/stations/{station_id}", json=payload)

            # Assert
            assert response.status_code == 200
            assert response.json() == {"status": "updated"}

            station = created["station"]
            assert isinstance(station, Station)
            assert station.id == station_id
            assert station.name == payload["name"]
            # location est optionnelle → None si non fournie
            assert station.location is None
            assert station.created_at is None

    class TestWhenRepositoryRaises:
        def test_returns_500_when_update_fails(
            self,
            client: TestClient,
            override_dependencies,
            fake_db,
            monkeypatch,
        ):
            class FailingRepository:
                def __init__(self, db):
                    pass

                def update_station(self, station):
                    raise RuntimeError("DB error")

            monkeypatch.setattr(
                controller_module,
                "Repository",
                FailingRepository,
            )

            station_id = 99
            payload = {
                "name": "Station KO",
                "location": "Lyon",
            }

            # Act
            response = client.put(f"/stations/{station_id}", json=payload)

            # Assert
            assert response.status_code == 500
            assert response.json()["detail"] == "Erreur interne"