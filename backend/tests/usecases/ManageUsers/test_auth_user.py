import pytest
from starlette.testclient import TestClient

from entities.repositories import Repository
from app import app
from infrastructure.database import get_db as get_db_dep
from google.oauth2 import id_token

from utils.omit import omit

import logging
from utils.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


@pytest.fixture(scope="function")
def client(tests_database):
    app.dependency_overrides[get_db_dep] = lambda: tests_database
    # app.dependency_overrides[get_current_user_from_bearer] = lambda: {"id": 1, "email": "test@example.com"}

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.pop(get_db_dep, None)
    # app.dependency_overrides.pop(get_current_user_from_bearer, None)

@pytest.fixture(scope="function")
def repo(tests_database) -> Repository:
    return Repository(tests_database)



class TestAuthUser:
    class TestWithoutBearerToken:
        def test_should_return_401(self, client):
            # Act
            resp = client.post("/api/auth/google")

            # Assert
            assert resp.status_code == 401
            data = resp.json()

            assert data == {'detail': 'Token manquant'}

    class TestWithBearerToken:
        class TestWhenVerify_oauth2_tokenSuccess:
            class TestVerifyOauth2TokenReturnEmail:
                def test_should_return_the_user(self, client, repo, monkeypatch):
                    # Arrange
                    monkeypatch.setattr(
                        id_token,
                        "verify_oauth2_token",
                        lambda token, request, client_id, clock_skew_in_seconds: {
                            "email": "test@example.com",
                            "sub": "fake-sub-id"
                        }
                    )

                    # Act
                    resp = client.post(
                        "/api/auth/google",
                        headers={"Authorization": "Bearer faketoken123"}
                    )

                    # Assert
                    # -- Assert a user is created
                    user_after = repo.get_user_by_email("test@example.com")
                    assert omit(user_after.__dict__, "id", "created_at") == {
                        "email": "test@example.com",
                        "google_sub": "fake-sub-id"
                    }

                    # -- Assert response contain tre created user
                    assert resp.status_code == 200
                    data = resp.json()
                    assert omit(data, "access_token") == {
                       "token_type": "bearer",
                       "user": {
                         "email": "test@example.com",
                         "id": user_after.id
                        }
                    }

                    # -- Assert cookies is created
                    cookies = resp.cookies

                    created_cookie = repo.get_token_by_id(cookies.get("refresh_id"))
                    assert created_cookie is not None
                    assert created_cookie.user_id == user_after.id
                    assert "refresh_id" in cookies

                    assert "HttpOnly" in resp.headers["set-cookie"]
                    assert "Path=/" in resp.headers["set-cookie"]


            class TestVerifyOauth2TokenDontReturnEmail:
                def test_should_return_400_information_user_invalid(self, client, repo, monkeypatch):
                    # Arrange
                    monkeypatch.setattr(
                        id_token,
                        "verify_oauth2_token",
                        lambda token, request, client_id, clock_skew_in_seconds: {
                            "sub": "fake-sub-id"
                        }
                    )

                    # Act
                    resp = client.post(
                        "/api/auth/google",
                        headers={"Authorization": "Bearer faketoken123"}
                    )

                    # Assert
                    assert resp.status_code == 400
                    data = resp.json()

                    assert repo.get_user_by_email("test@example.com") is None

                    assert omit(data, "access_token") == {
                        "detail": "Informations utilisateur incomplètes"
                    }

        class TestWhenVerify_oauth2_tokenFail:
            def test_should_return_401_token_invalide(self, client, repo, monkeypatch):
                # Arrange

                def fake_verify(token, request, client_id, clock_skew_in_seconds):
                    # tu peux mettre plus de logique ici
                    raise ValueError("This is a value error!")

                monkeypatch.setattr(id_token, "verify_oauth2_token", fake_verify)

                # Act
                resp = client.post(
                    "/api/auth/google",
                    headers={"Authorization": "Bearer faketoken123"}
                )

                # Assert
                assert resp.status_code == 401
                data = resp.json()

                assert data == {'detail': 'Token invalide'}

                assert repo.get_user_by_email("test@example.com") is None