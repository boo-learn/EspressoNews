import asyncio

from telethon import TelegramClient
from telethon.sessions import StringSession

from shared.celery_app import celery_app
from shared.config import RABBIT_HOST
from shared.db_utils import get_account_from_db
from shared.loggers import get_logger
from shared.rabbitmq import Producer, QueuesType, MessageData
from subscription_service.db_utils import subscribe_to_channel, unsubscribe_from_channel

logger = get_logger('subscription.tasks')


async def connect_and_execute(loaded_account, channel_username, action, action_name):
    local_logger = logger.bind(
        account=loaded_account.phone_number,
        channel=channel_username,
        action=action_name,
    )
    loaded_client = TelegramClient(StringSession(loaded_account.session_string), loaded_account.api_id,
                                   loaded_account.api_hash)
    try:
        await loaded_client.connect()
        local_logger.info('Client connected')
        await action(loaded_client, channel_username)
        local_logger.info('Action done')
    except Exception as e:
        logger.exception('Error occurred', error=e)
    finally:
        await loaded_client.disconnect()
        local_logger.info('Client disconnected')


def task_executor(account_id, channel_username, action, action_name, task_name):
    local_logger = logger.bind(task=task_name, account=account_id, channel=channel_username)
    local_logger.info('Starting task')
    loaded_account = get_account_from_db(account_id)
    if loaded_account:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(connect_and_execute(loaded_account, channel_username, action, action_name))
        loop.close()
        local_logger.info('Task completed')
    else:
        local_logger.error('Account not found')


@celery_app.task(name='tasks.subscribe_task', rate_limit='1/m', queue='subscription_queue')
def subscribe_task(account_id, channel_username):
    logger.info('Subscribing to channel', channel=channel_username)
    task_executor(account_id, channel_username, subscribe_to_channel, 'subscribe', 'subscribed')


@celery_app.task(name='tasks.unsubscribe_task', rate_limit='1/m', queue='subscription_queue')
def unsubscribe_task(account_id, channel_username):
    logger.info('Unsubscribing from channel', channel=channel_username)
    task_executor(account_id, channel_username, unsubscribe_from_channel, 'unsubscribe', 'unsubscribed')


async def send_to_subscribe_channel(type: str, msg: str):
    message: MessageData = {
        "type": type,
        "data": msg
    }
    producer = Producer(host=RABBIT_HOST, queue=QueuesType.subscription_service)
    await producer.send_message(message, QueuesType.subscription_service)
