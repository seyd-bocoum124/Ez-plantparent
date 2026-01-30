# tests/test_station_creation.py
from utils.omit import omit


class TestOmit:
    class TestWhenUserIsAdmin:
        def test_when_multiple_path_should_remove_them(self):
            # Arrange
            data = {"adresse": {"rue": "R", "ville": "Mtl"}, "autre": 1}

            # Act
            clean = omit(data, "adresse.ville", "adresse.rue")

            # Assert
            assert clean == {"autre": 1}

    class TestWhenUserIsNotAdmin:
        def test_when_a_list_with_a_nesting_prop(self):
            # Arrange
            data = {"items": [{"adresse": {"ville": "V1", "rue": "R1"}}, {"adresse": {"ville": "V2"}}]}

            # Act
            clean = omit(data, "items[*].adresse.ville")

            # Assert
            assert clean == {'items': [{'adresse': {'rue': 'R1'}}, {}]}

