import pytest
from fastapi.testclient import TestClient
from pydantic import TypeAdapter
from sqlalchemy import select
from shared.models import Category
from admin_service.core.const import CATEGORIES_URL as api_url
from admin_service import schemas
from admin_service.permissions.roles import Role


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
    assert categories[1]["name"] == categories_data[1]["name"]


def test_get_category_by_id(create_object, client: TestClient):
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


def test_create_category(client: TestClient, user_token_headers):
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


def test_category_update(session, create_object, client: TestClient, user_token_headers):
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
