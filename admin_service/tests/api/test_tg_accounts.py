from fastapi.testclient import TestClient
from pydantic import TypeAdapter
from sqlalchemy import select
from shared.models import TelegramAccount
from admin_service.core.const import TGACCOUNTS_URL
from admin_service import schemas


def test_get_tg_accounts(create_objects, client: TestClient):
    accounts_data = [
        {
            "api_id": 28122381,
            "api_hash": "eb1fc2cc4771b19abcf5e570e4b1fa2b",
            "phone_number": "+18629992207",
            "session_string": "1AZWarzsBuy8qxcdk8hZOrQz7x..."
        },
        {
            "api_id": 28092117,
            "api_hash": "404a4c4207ff2edf9ffa5f1ade087c77",
            "phone_number": "+18654335818",
            "session_string": "1AZWarzgBuzW-gqOAP7Uy5Fx9F..."
        },
        {
            "api_id": 26466645,
            "api_hash": "761af1c804deb5c5328ee784f78036c5",
            "phone_number": "+18654335178",
            "session_string": "1AZWarzgBu8RT0jhj-8WptoL2..."
        },
    ]
    create_objects(TelegramAccount, accounts_data)
    result = client.get(f"{TGACCOUNTS_URL}")
    accounts = result.json()
    assert result.status_code == 200
    # Проверяем соответствие аккаунтов схеме:
    ta = TypeAdapter(list[schemas.TgAccountSchema])
    ta.validate_python(accounts)
    assert len(accounts) == len(accounts_data)
    assert accounts[1]["api_id"] == accounts_data[1]["api_id"]


def test_get_tg_account_by_id(create_object, client: TestClient):
    account_data = {
        "api_id": 28122381,
        "api_hash": "eb1fc2cc4771b19abcf5e570e4b1fa2b",
        "phone_number": "+18629992207",
        "session_string": "1AZWarzsBuy8qxcdk8hZOrQz7x..."
    }

    create_object(TelegramAccount, account_data)
    result = client.get(f"{TGACCOUNTS_URL}/1")
    account = result.json()
    assert result.status_code == 200
    schemas.TgAccountSchema(**account)
    assert account["api_id"] == account_data["api_id"]


def test_get_tg_account_by_id_not_found(client: TestClient):
    result = client.get(f"{TGACCOUNTS_URL}/5")
    assert result.status_code == 404


def test_create_tg_account(client: TestClient, superuser_token_headers):
    account_data = {
        "api_id": 28122381,
        "api_hash": "eb1fc2cc4771b19abcf5e570e4b1fa2b",
        "phone_number": "+18629992207",
        "session_string": "1AZWarzsBuy8qxcdk8hZOrQz7x..."
    }
    result = client.post(f"{TGACCOUNTS_URL}", json=account_data, headers=superuser_token_headers)
    account = result.json()
    assert result.status_code == 200
    schemas.TgAccountSchema(**account)


def test_create_tg_account_without_auth(client: TestClient):
    account_data = {
        "api_id": 28122381,
        "api_hash": "eb1fc2cc4771b19abcf5e570e4b1fa2b",
        "phone_number": "+18629992207",
        "session_string": "1AZWarzsBuy8qxcdk8hZOrQz7x..."
    }
    result = client.post(f"{TGACCOUNTS_URL}", json=account_data)
    assert result.status_code == 401


def test_tg_account_update(session, create_object, client: TestClient, superuser_token_headers):
    account_data = {
        "api_id": 28122381,
        "api_hash": "eb1fc2cc4771b19abcf5e570e4b1fa2b",
        "phone_number": "+18629992207",
        "session_string": "1AZWarzsBuy8qxcdk8hZOrQz7x..."
    }
    edited_account_data = {
        "api_id": 9999,
        "phone_number": "+9999",
    }

    create_object(TelegramAccount, account_data)
    result = client.put(f"{TGACCOUNTS_URL}/1", json=edited_account_data, headers=superuser_token_headers)
    edited_account = result.json()
    assert result.status_code == 200
    assert edited_account["api_id"] == edited_account_data["api_id"]
    assert edited_account["api_hash"] == account_data["api_hash"]
    assert edited_account["phone_number"] == edited_account_data["phone_number"]
    assert edited_account["session_string"] == account_data["session_string"]


def test_tg_account_delete_without_auth(create_object, client: TestClient):
    account_data = {
        "api_id": 28122381,
        "api_hash": "eb1fc2cc4771b19abcf5e570e4b1fa2b",
        "phone_number": "+18629992207",
        "session_string": "1AZWarzsBuy8qxcdk8hZOrQz7x..."
    }
    create_object(TelegramAccount, account_data)
    result = client.delete(f"{TGACCOUNTS_URL}/1")
    assert result.status_code == 401


def test_tg_account_delete(session, create_object, client: TestClient, superuser_token_headers):
    account_data = {
        "api_id": 28122381,
        "api_hash": "eb1fc2cc4771b19abcf5e570e4b1fa2b",
        "phone_number": "+18629992207",
        "session_string": "1AZWarzsBuy8qxcdk8hZOrQz7x..."
    }
    create_object(TelegramAccount, account_data)
    result = client.delete(f"{TGACCOUNTS_URL}/1", headers=superuser_token_headers)
    assert result.status_code == 204
    assert session.scalar(select(TelegramAccount).where(TelegramAccount.api_id == account_data["api_id"])) is None
