from fastapi.testclient import TestClient
from pydantic import TypeAdapter
from sqlalchemy import select
from shared.models import GPTAccount
from admin_service.core.const import GPTACCOUNTS_URL
from admin_service import schemas
from admin_service.permissions.roles import Role


def test_get_gpt_accounts(create_objects, client: TestClient):
    accounts_data = [
        {
            "api_key": "111111111111",
        },
        {
            "api_key": "222222222222",
        },
        {
            "api_key": "333333333333",
        },

    ]
    create_objects(GPTAccount, accounts_data)
    result = client.get(f"{GPTACCOUNTS_URL}")
    accounts = result.json()
    assert result.status_code == 200
    # Проверяем соответствие аккаунтов схеме:
    ta = TypeAdapter(list[schemas.GPTAccountSchema])
    ta.validate_python(accounts)
    assert len(accounts) == len(accounts_data)
    assert accounts[1]["api_key"] == accounts_data[1]["api_key"]


def test_get_tg_account_by_id(create_object, client: TestClient):
    account_data = {
        "api_key": "111111111111",
    }

    create_object(GPTAccount, account_data)
    result = client.get(f"{GPTACCOUNTS_URL}/1")
    account = result.json()
    assert result.status_code == 200
    schemas.GPTAccountSchema(**account)
    assert account["api_key"] == account_data["api_key"]


def test_get_tg_account_by_id_not_found(client: TestClient):
    result = client.get(f"{GPTACCOUNTS_URL}/5")
    assert result.status_code == 404


def test_create_tg_account(client: TestClient, user_token_headers):
    account_data = {
        "api_key": "111111111111",
    }
    token_headers = user_token_headers(user_role=Role.ADMINISTRATOR)
    result = client.post(f"{GPTACCOUNTS_URL}", json=account_data, headers=token_headers)
    account = result.json()
    assert result.status_code == 200
    schemas.GPTAccountSchema(**account)


def test_create_tg_account_without_auth(client: TestClient):
    account_data = {
        "api_key": "111111111111",
    }
    result = client.post(f"{GPTACCOUNTS_URL}", json=account_data)
    assert result.status_code == 401


def test_tg_account_update(session, create_object, client: TestClient, user_token_headers):
    account_data = {
        "api_key": "111111111111",
    }
    edited_account_data = {
        "api_key": "1111111111112",
    }
    token_headers = user_token_headers(user_role=Role.ADMINISTRATOR)
    create_object(GPTAccount, account_data)
    result = client.put(f"{GPTACCOUNTS_URL}/1", json=edited_account_data, headers=token_headers)
    edited_account = result.json()
    assert result.status_code == 200
    assert edited_account["api_key"] == edited_account_data["api_key"]


def test_tg_account_delete_without_auth(create_object, client: TestClient):
    account_data = {
        "api_key": "111111111111",
    }
    create_object(GPTAccount, account_data)
    result = client.delete(f"{GPTACCOUNTS_URL}/1")
    assert result.status_code == 401


def test_tg_account_delete(session, create_object, client: TestClient, user_token_headers):
    account_data = {
        "api_key": "111111111111",
    }
    token_headers = user_token_headers(user_role=Role.ADMINISTRATOR)
    create_object(GPTAccount, account_data)
    result = client.delete(f"{GPTACCOUNTS_URL}/1", headers=token_headers)
    assert result.status_code == 204
    assert session.scalar(select(GPTAccount).where(GPTAccount.api_key == account_data["api_key"])) is None
