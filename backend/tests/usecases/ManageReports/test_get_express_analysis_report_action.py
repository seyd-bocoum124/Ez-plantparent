import pytest

from entities.exceptions import NotFoundException
from entities.models import ExpressAnalysisReport
from entities.repositories import Repository
from usecases.ManageReports.ExpressAnalysis.GetExpressAnalysisReport.GetExpressAnalysisReportAction import \
    GetExpressAnalysisReportAction


@pytest.fixture(scope="function")
def repository(tests_database) -> Repository:
    return Repository(tests_database)


@pytest.fixture(scope="function")
def action(repository) -> GetExpressAnalysisReportAction:
    # Couvre le chemin __init__ avec repo != None
    return GetExpressAnalysisReportAction(repo=repository)


class TestGetExpressAnalysisReportAction:
    class TestWhenReportExists:
        def test_should_return_the_report(self):
            # Arrange
            expected_report = ExpressAnalysisReport(
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

            class FakeRepository:
                def get_express_analysis_report_by_id(self, report_id: int):
                    # on vérifie qu'on reçoit bien l'ID demandé
                    assert report_id == 123
                    return expected_report

            action = GetExpressAnalysisReportAction(repo=FakeRepository())

            # Act
            report = action.execute(123)

            # Assert
            assert report is expected_report
            assert report.id == 123
            assert report.analysis_type == "express"

    class TestWhenReportDoesNotExist:
        def test_should_raise_not_found_exception(self, action: GetExpressAnalysisReportAction):
            # Arrange
            unknown_id = 999999

            # Act / Assert
            with pytest.raises(NotFoundException) as excinfo:
                action.execute(unknown_id)

            assert str(unknown_id) in str(excinfo.value)

    class TestInit:
        def test_when_repo_is_none_should_create_repository_from_get_db(self, monkeypatch):
            """
            Couvre le chemin __init__(repo=None) :
            - get_db() est appelé
            - Repository(db) est instancié et affecté à self.repo
            """

            import usecases.ManageReports.ExpressAnalysis.GetExpressAnalysisReport.GetExpressAnalysisReportAction as action_module

            fake_db = object()
            created = {}

            def fake_get_db():
                created["get_db_called"] = True
                return fake_db

            class FakeRepository:
                def __init__(self, db):
                    created["repo_db"] = db
                    created["instance"] = self

            # Patch des symboles dans le MODULE de l'action
            monkeypatch.setattr(action_module, "get_db", fake_get_db)
            monkeypatch.setattr(action_module, "Repository", FakeRepository)

            # Act
            action = action_module.GetExpressAnalysisReportAction(repo=None)

            # Assert
            assert created.get("get_db_called") is True
            assert created.get("repo_db") is fake_db
            assert isinstance(action.repo, FakeRepository)
            assert created.get("instance") is action.repo