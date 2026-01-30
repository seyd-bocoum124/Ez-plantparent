import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from entities.exceptions import NotFoundException
from infrastructure.database import get_db as get_db_dependency

import usecases.ManageReports.GetExpressAnalysisReport as controller_module

from usecases.ManageReports.ExpressAnalysis.ListAnalysisReports.Controller import (
    ExpressAnalysisReportOut,
)


@pytest.fixture(scope="function")
def app():
    """
    App FastAPI pour les tests, avec le router du controller.
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
    Override de la dépendance get_db utilisée dans le Controller.
    On override la fonction importée depuis infrastructure.database.
    """
    def _fake_get_db():
        return fake_db

    app.dependency_overrides[get_db_dependency] = _fake_get_db
    yield
    app.dependency_overrides.clear()


class TestGetExpressAnalysisReportController:
    class TestWhenReportExists:
        def test_returns_200_and_report(
            self,
            client: TestClient,
            override_dependencies,
            fake_db,
            monkeypatch,
        ):
            # Arrange : on construit un ExpressAnalysisReportOut complet
            expected = ExpressAnalysisReportOut(
                id=123,
                plant_id=1,
                analysis_type="express",
                soil_humidity_mean=10.5,
                lumens_mean=1234.0,
                air_humidity_mean=55.0,
                temperature_mean=22.3,
                soil_humidity_data="[10,11,10.5]",
                lumens_data="[1200,1250,1234]",
                air_humidity_data="[50,55,60]",
                temperature_data="[22,22.5,22.3]",
                created_at=None,
            )

            created = {}

            class FakeAction:
                def __init__(self, repository):
                    # On vérifie qu’on reçoit bien un repo basé sur fake_db
                    created["repo"] = repository

                def execute(self, report_id: int):
                    # On vérifie l’ID reçu via l’URL
                    assert report_id == expected.id
                    return expected

            # On remplace la vraie action par notre fake
            monkeypatch.setattr(
                controller_module,
                "GetExpressAnalysisReportAction",
                FakeAction,
            )

            # Act
            response = client.get(f"/reports/express-analysis/{expected.id}")

            # Assert
            assert response.status_code == 200
            body = response.json()

            # On ne suppose pas quels champs sont exposés par le response_model :
            # on vérifie juste que pour chaque clé de la réponse,
            # la valeur correspond à l'attribut de l'objet expected.
            for key, value in body.items():
                assert getattr(expected, key) == value

            # On vérifie qu’un repository a bien été instancié
            assert "repo" in created

    class TestWhenReportNotFound:
        def test_returns_404_when_not_found(
            self,
            client: TestClient,
            override_dependencies,
            monkeypatch,
        ):
            # Arrange
            class FakeAction:
                def __init__(self, repository):
                    pass

                def execute(self, report_id: int):
                    raise NotFoundException(f"Report {report_id} not found")

            monkeypatch.setattr(
                controller_module,
                "GetExpressAnalysisReportAction",
                FakeAction,
            )

            # Act
            response = client.get("/reports/express-analysis/999999")

            # Assert
            assert response.status_code == 404
            body = response.json()
            assert "detail" in body


    class TestWhenUnexpectedError:
        def test_returns_500_on_unexpected_error(
            self,
            client: TestClient,
            override_dependencies,
            monkeypatch,
        ):
            # Arrange
            class FakeAction:
                def __init__(self, repository):
                    pass

                def execute(self, report_id: int):
                    raise RuntimeError("Boom!")

            monkeypatch.setattr(
                controller_module,
                "GetExpressAnalysisReportAction",
                FakeAction,
            )

            # Act
            response = client.get("/reports/express-analysis/123")

            # Assert
            assert response.status_code == 500
            # On colle exactement au message défini dans ton Controller.py
            assert (
                response.json()["detail"]
                == "Une erreure interne s'est produite!"
            )