from dataclasses import asdict

import pytest

from usecases.ManageStations.CreateStation.CreateStationAction import (
    CreateStationAction, CreateStationParams,
)
from entities.repositories import Repository
from utils.logging_config import setup_logging
from utils.omit import omit
import logging
setup_logging()
logger = logging.getLogger(__name__)

@pytest.fixture(scope="function")
def repository(tests_database):
    return Repository(tests_database)

@pytest.fixture(scope="function")
def action(repository):
    return CreateStationAction(repo=repository)

from pydantic import ValidationError as PydanticValidationError
class TestCreateStationParams:
    class TestWhenAEmptyParams:
        def test_should_throw_a_validation_error(self):
            # Act
            with pytest.raises(PydanticValidationError) as excinfo:
                CreateStationParams(name="", location="a-location")

            # Assert
            assert any(
                e['loc']== ("name",) and e['type'] == "string_too_short"
                for e in excinfo.value.errors()
            )

class TestCreateStationAction:
    class TestWhenBadParams:
        def test_should_record_a_station_and_return_it(self, repository, action: CreateStationAction):
            # Arrange
            params = CreateStationParams(user_id=1, name="Boreal", location="loc2")

            # Act
            station = action.execute(params)

            # Assert
            assert omit(asdict(station), "id", "created_at", "pairing_code", "mac_adress", "pairing_timeout") == {'user_id': 1, 'location': 'loc2', 'name': 'Boreal'}
            assert station == repository.get_station_by_id(station.id)
