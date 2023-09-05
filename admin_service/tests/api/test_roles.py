import pytest
from loguru import logger

from sqlalchemy import create_engine, select, func, insert, Table, inspect
from fastapi.testclient import TestClient
from admin_service import schemas
from admin_service.models.admin_user import AdminUser
from admin_service.permissions.roles import Role
from admin_service.core.const import CATEGORIES_URL


# @pytest.mark.skip()
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


def test_create_category_without_permission(user_token_headers, client: TestClient):
    token_headers = user_token_headers(user_role=Role.USER)
    result = client.post(f"{CATEGORIES_URL}", headers=token_headers)
    assert result.status_code == 403
