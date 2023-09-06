import pytest
from collections.abc import Callable
from fastapi.testclient import TestClient
from pydantic import TypeAdapter
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from shared.models import Category, User, Base
from admin_service.core.const import CATEGORIES_URL as api_url
from admin_service import schemas
from admin_service.permissions.roles import Role


# TODO: разобраться с SAWarning вместо игнорирования
@pytest.mark.filterwarnings("ignore::sqlalchemy.exc.SAWarning")
def test_get_categories(create_objects, client: TestClient):
    categories_data = [
        {
            "name": "Мирные"
        },
        {
            "name": "Мафия"
        },
    ]
    create_objects(Category, categories_data)
    result = client.get(f"{api_url}")
    categories = result.json()
    assert result.status_code == 200
    # Проверяем соответствие аккаунтов схеме:
    ta = TypeAdapter(list[schemas.CategorySchema])
    ta.validate_python(categories)
    assert len(categories) == len(categories_data)


def test_get_category_by_id(create_object: Callable, client: TestClient):
    category_data = {
        "name": "Мирные"
    }
    create_object(Category, category_data)
    result = client.get(f"{api_url}/1")
    category = result.json()
    assert result.status_code == 200
    schemas.CategorySchema(**category)
    assert category["name"] == category_data["name"]


def test_get_category_by_id_not_found(client: TestClient):
    result = client.get(f"{api_url}/5")
    assert result.status_code == 404


def test_create_category(client: TestClient, user_token_headers: Callable):
    category_data = {
        "name": "Мирные"
    }
    token_headers = user_token_headers(user_role=Role.ADMINISTRATOR)
    result = client.post(f"{api_url}", json=category_data, headers=token_headers)
    account = result.json()
    assert result.status_code == 200
    schemas.CategorySchema(**account)


def test_create_category_without_auth(client: TestClient):
    category_data = {
        "name": "Мирные"
    }
    result = client.post(f"{api_url}", json=category_data)
    assert result.status_code == 401


def test_category_update(create_object, client: TestClient, user_token_headers):
    category_data = {
        "name": "Мирные"
    }
    edited_category_data = {
        "name": "Злыдни"
    }
    token_headers = user_token_headers(user_role=Role.ADMINISTRATOR)
    create_object(Category, category_data)
    result = client.put(f"{api_url}/1", json=edited_category_data, headers=token_headers)
    edited_category = result.json()
    assert result.status_code == 200
    assert edited_category["name"] == edited_category["name"]


def test_category_add_relation_to_users(session, client: TestClient, create_objects, user_token_headers):
    categories_data = [
        {"id": 1, "name": "People"},
        {"id": 2, "name": "Beast"}
    ]
    tg_users_data = [
        {"user_id": 1, "username": "Alex"},
        {"user_id": 2, "username": "Wolf"},
        {"user_id": 3, "username": "WereWolf"},
    ]
    token_headers = user_token_headers(user_role=Role.MARKETER)
    create_objects(Category, categories_data)
    create_objects(User, tg_users_data)
    result1 = client.put(f"{api_url}/1/users", json=[1, 3], headers=token_headers)
    assert result1.status_code == 204
    result2 = client.put(f"{api_url}/2/users", json=[2, 3], headers=token_headers)
    assert result2.status_code == 204
    user_alex = session.get(User, 1)
    user_wolf = session.get(User, 2)
    user_were_wolf = session.get(User, 3)
    assert len(user_alex.categories) == 1
    assert len(user_wolf.categories) == 1
    assert len(user_were_wolf.categories) == 2


@pytest.mark.filterwarnings("ignore::sqlalchemy.exc.SAWarning")
def test_category_for_user_already_exist(client: TestClient, create_object, user_token_headers):
    category_data = {
        "id": 1, "name": "Мирные"
    }
    tg_user_data = {
        "user_id": 1, "username": "Alex",
        "categories": [
            Category(**category_data)
        ]
    }
    token_headers = user_token_headers(user_role=Role.MARKETER)
    create_object(User, tg_user_data)
    result = client.put(f"{api_url}/1/users", json=[1], headers=token_headers)
    assert result.status_code == 400


@pytest.mark.filterwarnings("ignore::sqlalchemy.exc.SAWarning")
def test_category_for_user_undefined(client: TestClient, create_object, user_token_headers):
    tg_user_data = {
        "user_id": 1, "username": "Alex",
    }
    token_headers = user_token_headers(user_role=Role.MARKETER)
    create_object(User, tg_user_data)
    result = client.put(f"{api_url}/1/users", json=[1], headers=token_headers)
    assert result.status_code == 404


def test_category_delete_without_auth(create_object, client: TestClient):
    category_data = {
        "name": "Мирные"
    }
    create_object(Category, category_data)
    result = client.delete(f"{api_url}/1")
    assert result.status_code == 401


def test_category_delete(session, create_object, client: TestClient, user_token_headers):
    category_data = {
        "name": "Мирные"
    }
    token_headers = user_token_headers(user_role=Role.ADMINISTRATOR)
    create_object(Category, category_data)
    result = client.delete(f"{api_url}/1", headers=token_headers)
    assert result.status_code == 204
    assert session.scalar(select(Category).where(Category.name == category_data["name"])) is None
