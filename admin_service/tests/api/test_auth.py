from loguru import logger
from fastapi.testclient import TestClient
from admin_service.core.const import TOKEN_TYPE


def test_get_access_token(load_data_from_json, client: TestClient):
    load_data_from_json("users_dataset01.json")
    login_data = {
        "username": "test2@mail.ru",
        "password": "test",
    }
    result = client.post(f"/auth/login/access-token", data=login_data)
    token = result.json()
    assert result.status_code == 200
    assert "access_token" in token
    assert token["token_type"] == TOKEN_TYPE


def test_get_access_token_undefined_user(load_data_from_json, client: TestClient):
    load_data_from_json("users_dataset01.json")
    login_data = {
        "username": "test10@mail.ru",
        "password": "test",
    }
    result = client.post(f"/auth/login/access-token", data=login_data)
    logger.info(result.json())
    assert result.status_code == 400


def test_use_access_token(
    client: TestClient, superuser_token_headers
):
    result = client.post(
        f"/auth/login/test-token", headers=superuser_token_headers,
    )
    user = result.json()
    assert result.status_code == 200
    assert "email" in user
