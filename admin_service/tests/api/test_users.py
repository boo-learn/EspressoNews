from sqlalchemy import create_engine, select, func, insert, Table, inspect
from fastapi.testclient import TestClient
from admin_service import models


# @pytest.mark.skip()
def test_get_users(session, load_data_from_json, client: TestClient):
    load_data_from_json("users_dataset01.json")
    # admin_user: models.AdminUser = session.scalar(select(models.AdminUser).where(models.AdminUser.id == 2))
    result = client.get("/users")
    users = result.json()
    assert users[1]["id"] == 2
    assert users[1]["email"] == "test2@mail.ru"
    assert users[1]["name"] == "test-user2"
    # assert models.AdminUser.verify_password("test", users[1]["hashed_password"])
