import pytest
from loguru import logger

from sqlalchemy import create_engine, select, func, insert, Table, inspect
from fastapi.testclient import TestClient
from admin_service import schemas
from admin_service.models.admin_user import AdminUser


# @pytest.mark.skip()
def test_get_users(load_data_from_json, client: TestClient):
    load_data_from_json("users_dataset01.json")
    result = client.get("/users")
    users = result.json()
    assert result.status_code == 200
    assert len(users) == 4
    assert "id" in users[1]
    assert users[1]["email"] == "test2@mail.ru"
    assert users[1]["name"] == "test-user2"
    # assert AdminUser.verify_password("test", users[1]["hashed_password"])


def test_get_user_by_id(load_data_from_json, client: TestClient):
    load_data_from_json("users_dataset01.json")
    result = client.get("/users/2")
    user = result.json()
    assert result.status_code == 200
    assert user["email"] == "test2@mail.ru"


def test_get_user_by_id_not_found(client: TestClient):
    result = client.get("/users/10")
    assert result.status_code == 404


def test_create_user_without_auth(client: TestClient):
    user_data = {
        "name": "test-user1",
        "email": "test1@mail.ru",
        "password": "test"
    }
    result = client.post(
        "/users", json=user_data
    )
    logger.info(result.json())
    assert result.status_code == 401


# @pytest.mark.skip()
def test_create_user(client: TestClient, superuser_token_headers):
    user_data = {
        "name": "test-user1",
        "email": "test1@mail.ru",
        "password": "test"
    }
    result = client.post(
        "/users", json=user_data, headers=superuser_token_headers
    )
    result_user: dict = result.json()

    assert result.status_code == 201
    assert result_user["email"] == user_data["email"]
    assert "id" in result_user
    assert "password" not in result_user


def test_create_user_already_exist(
        load_data_from_json,
        client: TestClient,
        superuser_token_headers
):
    load_data_from_json("users_dataset01.json")
    user_data = {
        "name": "test-user1",
        "email": "test1@mail.ru",
        "password": "test"
    }
    result = client.post(
        "/users", json=user_data, headers=superuser_token_headers
    )
    assert result.status_code == 400
