import pytest

from fastapi.testclient import TestClient
from admin_service.core.config import settings
from admin_service.models.admin_user import AdminUser
from admin_service.permissions.roles import Role


# @pytest.fixture
# def user_token_headers(create_object, request):
#     pass

# @pytest.fixture()
# def get_auth_token():
#     login_data = {
#         "username": settings.FIRST_SUPERUSER_EMAIL,
#         "password": settings.FIRST_SUPERUSER_PASSWORD,
#     }
#     r = client.post(f"/auth/login/access-token", data=login_data)
#     tokens = r.json()
#     a_token = tokens["access_token"]
#     headers = {"Authorization": f"Bearer {a_token}"}
#     return headers


@pytest.fixture(scope="function")
def user_token_headers(create_object, client):
    def _user_token_headers(user_role: Role) -> dict[str, str]:
        """
        Create and login AdminUser with a given role
        """
        user_data = {
            "name": "auth_test_user",
            "email": "auth_test_user@testmail.ru",
            "password": "auth_test_user",
            "role": user_role
        }
        create_object(AdminUser, user_data)
        login_data = {
            "username": user_data["email"],
            "password": user_data["password"],
        }
        r = client.post(f"/auth/login/access-token", data=login_data)
        tokens = r.json()
        a_token = tokens["access_token"]
        headers = {"Authorization": f"Bearer {a_token}"}
        return headers

    return _user_token_headers

# @pytest.fixture()
# def superuser(create_object) -> AdminUser:
#     user_data = {
#         "name": settings.FIRST_SUPERUSER_NAME,
#         "email": settings.FIRST_SUPERUSER_EMAIL,
#         "password": settings.FIRST_SUPERUSER_PASSWORD,
#         "role": Role.USER,
#     }
#     return create_object(AdminUser, user_data)
#
#
# @pytest.fixture()
# def marketer_user(create_object) -> AdminUser:
#     user_data = {
#         "name": "marketer",
#         "email": "marketer@testmail.ru",
#         "password": "marketer",
#         "role": Role.MARKETER,
#     }
#     return create_object(AdminUser, user_data)
#
#
# @pytest.fixture()
# def superuser_token_headers(client: TestClient, superuser) -> dict[str, str]:
#     login_data = {
#         "username": settings.FIRST_SUPERUSER_EMAIL,
#         "password": settings.FIRST_SUPERUSER_PASSWORD,
#     }
#     r = client.post(f"/auth/login/access-token", data=login_data)
#     tokens = r.json()
#     a_token = tokens["access_token"]
#     headers = {"Authorization": f"Bearer {a_token}"}
#     return headers
#
#
# @pytest.fixture()
# def marketer_user_token_headers(client: TestClient, superuser) -> dict[str, str]:
#     login_data = {
#         "username": "marketer@testmail.ru",
#         "password": "marketer",
#     }
#     r = client.post(f"/auth/login/access-token", data=login_data)
#     tokens = r.json()
#     a_token = tokens["access_token"]
#     headers = {"Authorization": f"Bearer {a_token}"}
#     return headers
