import logging
from telethon import TelegramClient
from telethon.sessions import StringSession

from shared.db_utils import (get_account_from_db_async)
from shared.celery_app import subscriptions_celery_app
from db_utils import subscribe_to_channel, unsubscribe_from_channel

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@subscriptions_celery_app.task(queue='normal_priority')
async def subscribe_task(account_id, channel_username):
    logger.info(f'Starting subscription task for account {account_id} and channel {channel_username}')
    loaded_account = await get_account_from_db_async(account_id)
    if loaded_account:
        loaded_client = TelegramClient(StringSession(loaded_account.session_string), loaded_account.api_id,
                                       loaded_account.api_hash)
        await loaded_client.connect()
        await subscribe_to_channel(loaded_client, channel_username)
        await loaded_client.disconnect()
        logger.info(f'Successfully subscribed account {account_id} to channel {channel_username}')
    else:
        logger.error(f'Account {account_id} not found')


@subscriptions_celery_app.task
async def unsubscribe_task(account_id, channel_username):
    logger.info(f'Starting unsubscription task for account {account_id} and channel {channel_username}')
    loaded_account = await get_account_from_db_async(account_id)
    if loaded_account:
        loaded_client = TelegramClient(StringSession(loaded_account.session_string), loaded_account.api_id,
                                       loaded_account.api_hash)
        await loaded_client.connect()
        await unsubscribe_from_channel(loaded_client, channel_username)
        await loaded_client.disconnect()
        logger.info(f'Successfully unsubscribed account {account_id} from channel {channel_username}')
    else:
        logger.error(f'Account {account_id} not found')
