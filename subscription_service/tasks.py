import logging

from telethon import TelegramClient
from telethon.sessions import StringSession

from shared.db_utils import (get_account_from_db_async)
from subscription_service.db_utils import subscribe_to_channel

from shared.celery_app import celery_app
from asgiref.sync import async_to_sync

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@celery_app.task(name='tasks.subscribe_task')
def subscribe_task(account_id, channel_username):
    logger.info(f'Starting subscription task for account {account_id} and channel {channel_username}')
    loaded_account = async_to_sync(get_account_from_db_async)(account_id)
    if loaded_account:
        logger.info('Have logged acount')
        loaded_client = TelegramClient(StringSession(loaded_account.session_string), loaded_account.api_id,
                                       loaded_account.api_hash)
        logger.info('Get telegram client')
        async_to_sync(loaded_client.connect)()
        async_to_sync(subscribe_to_channel)(loaded_client, channel_username)
        logger.info('subscribe start ok!')
        async_to_sync(loaded_client.disconnect)()
        logger.info(f'Successfully subscribed account {account_id} to channel {channel_username}')
    else:
        logger.error(f'Account {account_id} not found')
