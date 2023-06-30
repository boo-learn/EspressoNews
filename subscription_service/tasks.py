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
    try:
        loaded_client = TelegramClient(StringSession(loaded_account.session_string), loaded_account.api_id,
                                    loaded_account.api_hash)
        logger.info('Created telegram client for account: %s', loaded_account.username)
        await loaded_client.connect()
        logger.info('Connected to telegram for account: %s', loaded_account.username)
        await subscribe_to_channel(loaded_client, channel_username)
        logger.info('Subscribed account: %s to channel: %s', loaded_account.username, channel_username)
        await loaded_client.disconnect()
        logger.info('Disconnected from telegram for account: %s', loaded_account.username)
    except Exception as e:
        logger.error('Error in connect_and_subscribe for account: %s, Error: %s', loaded_account.username, str(e))

@celery_app.task(name='tasks.subscribe_task')
def subscribe_task(account_id, channel_username):
    logger.info('Starting subscription task for account: %s and channel: %s', account_id, channel_username)
    loaded_account = get_account_from_db(account_id)
    if loaded_account:
        logger.info('Loaded account: %s from database', loaded_account.username)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(connect_and_subscribe(loaded_account, channel_username))
            logger.info('Successfully subscribed account: %s to channel: %s', account_id, channel_username)
        except Exception as e:
            logger.error('Error in subscribe_task for account: %s, Error: %s', account_id, str(e))
        finally:
            loop.close()
    else:
        logger.error('Account not found in database: %s', account_id)