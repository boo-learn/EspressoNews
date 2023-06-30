import asyncio
import logging

from telethon import TelegramClient
from telethon.sessions import StringSession

from shared.db_utils import (get_account_from_db)
from subscription_service.db_utils import subscribe_to_channel

from shared.celery_app import celery_app
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def connect_and_subscribe(loaded_account, channel_username):
    loaded_client = TelegramClient(StringSession(loaded_account.session_string), loaded_account.api_id,
                                   loaded_account.api_hash)
    logger.info('Get telegram client')
    await loaded_client.connect()
    await subscribe_to_channel(loaded_client, channel_username)
    logger.info('subscribe start ok!')
    await loaded_client.disconnect()

@celery_app.task(name='tasks.subscribe_task')
def subscribe_task(account_id, channel_username):
    logger.info(f'Starting subscription task for account {account_id} and channel {channel_username}')
    loaded_account = get_account_from_db(account_id)
    if loaded_account:
        logger.info('Have logged account')
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(connect_and_subscribe(loaded_account, channel_username))
        loop.close()
        logger.info(f'Successfully subscribed account {account_id} to channel {channel_username}')
    else:
        logger.error(f'Account {account_id} not found')