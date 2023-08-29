import pytest

from fastapi.testclient import TestClient
from admin_service.core.config import settings
from admin_service import models


@pytest.fixture()
def superuser(create_object) -> models.AdminUser:
    user_data = {
        "name": settings.FIRST_SUPERUSER_NAME,
        "email": settings.FIRST_SUPERUSER_EMAIL,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    return create_object(models.AdminUser, user_data)


@pytest.fixture()
def superuser_token_headers(client: TestClient, superuser) -> dict[str, str]:
    login_data = {
        "username": settings.FIRST_SUPERUSER_EMAIL,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    r = client.post(f"/auth/login/access-token", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers
