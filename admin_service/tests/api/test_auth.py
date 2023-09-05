from loguru import logger
from fastapi.testclient import TestClient
from admin_service.core.const import TOKEN_TYPE
from admin_service.permissions.roles import Role
from admin_service.models.admin_user import AdminUser


def test_get_access_token(create_object, client: TestClient):
    user_data = {
        "name": "test-user1",
        "email": "test1@mail.ru",
        "password": "test",
        "role": Role.ADMINISTRATOR
    }
    create_object(AdminUser, user_data)
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"],
    }
    result = client.post(f"/auth/login/access-token", data=login_data)
    token = result.json()
    assert result.status_code == 200
    assert "access_token" in token
    assert token["token_type"] == TOKEN_TYPE


def test_get_access_token_undefined_user(create_object, client: TestClient):
    login_data = {
        "username": "test10@mail.ru",
        "password": "test",
    }
    result = client.post(f"/auth/login/access-token", data=login_data)
    logger.info(result.json())
    assert result.status_code == 400


def test_use_access_token(
    client: TestClient, user_token_headers
):
    token_headers = user_token_headers(user_role=Role.ADMINISTRATOR)
    result = client.post(
        f"/auth/login/test-token", headers=token_headers,
    )
    user = result.json()
    assert result.status_code == 200
    assert "email" in user
