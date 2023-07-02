import asyncio
import logging
from telethon import TelegramClient
from telethon.sessions import StringSession
from shared.db_utils import get_account_from_db
from subscription_service.db_utils import subscribe_to_channel, unsubscribe_from_channel
from shared.celery_app import celery_app
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def connect_and_execute(loaded_account, channel_username, action, action_name):
    loaded_client = TelegramClient(StringSession(loaded_account.session_string), loaded_account.api_id,
                                   loaded_account.api_hash)
    try:
        await loaded_client.connect()
        logger.info(f'{action_name} start ok!')
        await action(loaded_client, channel_username)
    except ValueError as e:
        logger.error(f'Loaded account details: {loaded_account.__dict__}')
        logger.error(f'Channel username: {channel_username}')
    await loaded_client.disconnect()


def task_executor(account_id, channel_username, action, action_name, task_name):
    logger.info(f'Starting {task_name} for account {account_id} and channel {channel_username}')
    loaded_account = get_account_from_db(account_id)
    if loaded_account:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(connect_and_execute(loaded_account, channel_username, action, action_name))
        loop.close()
        logger.info(f'Successfully {task_name} account {account_id} to channel {channel_username}')
    else:
        logger.error(f'Account {account_id} not found')


@celery_app.task(name='tasks.subscribe_task', rate_limit='1/m')
def subscribe_task(account_id, channel_username):
    task_executor(account_id, channel_username, subscribe_to_channel, 'subscribe', 'subscribed')


@celery_app.task(name='tasks.unsubscribe_task', rate_limit='1/m')
def unsubscribe_task(account_id, channel_username):
    task_executor(account_id, channel_username, unsubscribe_from_channel, 'unsubscribe', 'unsubscribed')
