from telethon import TelegramClient
from telethon.sessions import StringSession

from shared.db_utils import (get_account_from_db_async)
from shared.celery_app import subscriptions_celery_app
from db_utils import subscribe_to_channel, unsubscribe_from_channel


@subscriptions_celery_app.task
async def subscribe_task(account_id, channel_username):
    loaded_account = await get_account_from_db_async(account_id)
    if loaded_account:
        loaded_client = TelegramClient(StringSession(loaded_account.session_string), loaded_account.api_id,
                                       loaded_account.api_hash)
        await loaded_client.connect()
        await subscribe_to_channel(loaded_client, channel_username)
        await loaded_client.disconnect()
    else:
        print("Account not found")


@subscriptions_celery_app.task
async def unsubscribe_task(account_id, channel_username):
    loaded_account = await get_account_from_db_async(account_id)
    if loaded_account:
        loaded_client = TelegramClient(StringSession(loaded_account.session_string), loaded_account.api_id,
                                       loaded_account.api_hash)
        await loaded_client.connect()
        await unsubscribe_from_channel(loaded_client, channel_username)
        await loaded_client.disconnect()
    else:
        print("Account not found")