import pytest
from loguru import logger

from sqlalchemy import create_engine, select, func, insert, Table, inspect
from fastapi.testclient import TestClient
from admin_service import schemas
from admin_service.permissions.roles import Role
from admin_service.models.admin_user import AdminUser


# @pytest.mark.skip()
def test_get_users(create_objects, client: TestClient):
    users_data = [
        {
            "email": "test1@mail.ru",
            "name": "test-user1",
            "password": "test",
            "role": Role.USER
        },
        {
            "email": "test2@mail.ru",
            "name": "test-user2",
            "password": "test",
            "role": Role.USER
        },
        {
            "email": "test3@mail.ru",
            "name": "test-user3",
            "password": "test",
            "role": Role.USER
        }
    ]
    create_objects(AdminUser, users_data)
    result = client.get("/users")
    users = result.json()
    assert result.status_code == 200
    assert len(users) == len(users_data)
    assert "id" in users[1]
    assert users[1]["email"] == users_data[1]["email"]
    assert users[1]["name"] == users_data[1]["name"]


def test_get_user_by_id(create_object, client: TestClient):
    user_data = {
        "name": "test-user1",
        "email": "test1@mail.ru",
        "password": "test",
        "role": Role.ADMINISTRATOR
    }
    create_object(AdminUser, user_data)
    result = client.get("/users/1")
    user = result.json()
    assert result.status_code == 200
    assert user["email"] == user_data["email"]


def test_get_user_by_id_not_found(client: TestClient):
    result = client.get("/users/10")
    assert result.status_code == 404


def test_create_user_without_auth(client: TestClient):
    user_data = {
        "name": "test-user1",
        "email": "test1@mail.ru",
        "password": "test",
        "role": Role.ADMINISTRATOR
    }
    result = client.post(
        "/users", json=user_data
    )
    logger.info(result.json())
    assert result.status_code == 401


# @pytest.mark.skip()
def test_create_user(client: TestClient, user_token_headers):
    user_data = {
        "name": "test-user1",
        "email": "test1@mail.ru",
        "password": "test",
        "role": Role.USER
    }
    token_headers = user_token_headers(user_role=Role.ADMINISTRATOR)
    logger.info(f"{token_headers=}")
    result = client.post(
        "/users", json=user_data, headers=token_headers
    )
    result_user: dict = result.json()

    assert result.status_code == 201
    assert result_user["email"] == user_data["email"]
    assert "id" in result_user
    assert "password" not in result_user


def test_create_user_already_exist(
        create_object,
        client: TestClient,
        user_token_headers
):
    user_data = {
        "name": "test-user1",
        "email": "test1@mail.ru",
        "password": "test",
        "role": Role.ADMINISTRATOR
    }
    create_object(AdminUser, user_data)
    token_headers = user_token_headers(user_role=Role.ADMINISTRATOR)
    result = client.post(
        "/users", json=user_data, headers=token_headers
    )
    assert result.status_code == 400
