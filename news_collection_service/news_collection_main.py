import asyncio
import datetime
import json

import pytz
from sqlalchemy.exc import IntegrityError
from telethon import TelegramClient
from telethon import events
from telethon.sessions import StringSession
from telethon.tl.types import Message

from db_utils import add_post_async, get_all_channels
from shared.db_utils import (
    get_account_from_db_async, get_all_accounts_from_db_async
)
from shared.models import Post
from shared.loggers import get_logger
import redis.asyncio as redis

logger = get_logger('collector.main')


async def create_redis_pool():
    pool = redis.ConnectionPool(host='redis', port=6379, db=0)
    r = redis.Redis(connection_pool=pool)
    return r


async def add_post_to_redis(redis_pool, post):
    async with redis_pool.pipeline(transaction=True) as pipe:
        await pipe.rpush('posts', post)
        await pipe.execute()


async def listen_to_account(account, redis_pool):
    account_logger = logger.bind(account=account.account_id)
    account_logger.debug('Initiating Telegram client')
    client = TelegramClient(StringSession(account.session_string), account.api_id, account.api_hash)
    client.parse_mode = None

    @client.on(events.NewMessage)
    async def my_event_handler(event: Message):
        account_logger.debug('Received new message', text=event.text)
        if event.is_channel:
            account_logger.debug('Received new channel message', event_id=event.id, channel_id=event.peer_id.channel_id)
            if event.text:
                # Add a check for the number of words in the message
                # words = event.text.split()
                # if len(words) < 9:
                #     logger.info(f'Skipping message {event.id} due to insufficient word count')
                #     return
                # If the word count is sufficient, process the message
                # post = Post(
                #     post_id=event.id,
                #     channel_id=event.peer_id.channel_id,
                #     rubric_id=None,
                #     title=event.text[:50] if event.text else "No title",
                #     content=event.text,
                #     post_date=event.date.astimezone(pytz.utc).replace(tzinfo=None) + datetime.timedelta(hours=3)
                # )
                post_json = json.dumps(
                    {
                        "post_id": event.id,
                        "channel_id": event.peer_id.channel_id,
                        "rubric_id": None,
                        "title": event.text[:50] if event.text else "No title",
                        "content": event.text,
                        "post_date": event.date.astimezone(pytz.utc).replace(tzinfo=None).isoformat(),
                    }
                )
                try:
                    await add_post_to_redis(redis_pool, post_json)
                except IntegrityError as e:
                    account_logger.error(f"Failed to add post", error=e)
                    return

    max_retries = 50
    current_retry = 0

    while current_retry < max_retries:
        try:
            await client.connect()
            account_logger.debug(f'Connected Telegram client')
            account_logger.info(f'Start listening')

            # Start the connection checker
            asyncio.create_task(check_connection(client))
            await client.run_until_disconnected()
            account_logger.debug(f'Disconnected client')
            break  # If we reach here, the disconnection was planned, so we exit the loop
        except Exception as e:
            account_logger.error('Error occurred, retrying in 5 seconds', error=e)
            await asyncio.sleep(5)  # Wait for 5 seconds before retrying
            current_retry += 1

    if current_retry >= max_retries:
        logger.error('Maximum retries reached. Exiting.')


async def check_connection(client):
    while True:
        try:
            me = await client.get_me()
            logger.info(f'Current user: {me.username}')
        except Exception as e:
            logger.error(f'Error occurred during connection check, retrying in 5 seconds', error=e)
            await client.connect()
        await asyncio.sleep(60)  # Check the connection every 10 seconds


async def main():
    logger.info(f'Collect news service run')
    logger.debug(f'Getting accounts for channels')
    await asyncio.sleep(30)
    redis_pool = await create_redis_pool()
    accounts = await get_all_accounts_from_db_async()
    logger.debug(f'Received {len(accounts)} accounts for channels')
    tasks = [listen_to_account(account, redis_pool) for account in accounts]
    logger.debug(f'Initiating listening tasks for {len(tasks)} accounts')
    await asyncio.gather(*tasks)
    logger.debug(f'Finished initiating listening tasks')


if __name__ == "__main__":
    logger.info(f'Starting main loop')
    loop = asyncio.get_event_loop()
    try:
        logger.debug(f'Creating main task')
        loop.create_task(main())
        logger.debug(f'Running event loop')
        loop.run_forever()
    finally:
        logger.info("Closing the event loop...")
        loop.close()
