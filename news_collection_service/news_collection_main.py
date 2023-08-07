import asyncio
import datetime
import logging

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

logger = logging.getLogger(__name__)
# Set the level of this logger to DEBUG,
# so that it will log all messages of level DEBUG and above
logger.setLevel(logging.DEBUG)

# Create a console handler that logs all messages
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Create a formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Add the formatter to the handler
console_handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(console_handler)


async def listen_to_account(account):
    logger.debug(f'Initiating Telegram client for account {account.account_id}')
    client = TelegramClient(StringSession(account.session_string), account.api_id, account.api_hash)
    client.parse_mode = None

    @client.on(events.NewMessage)
    async def my_event_handler(event: Message):
        logger.debug(f'Received new message {event.to_dict()}')
        logger.debug(f'Message text: {event.text}')
        if event.is_channel:
            logger.debug(f'Received new message on channel. Event id: {event.id}')
            logger.debug(f'Event channel id: {event.peer_id.channel_id}')
            if event.text:
                # Add a check for the number of words in the message
                # words = event.text.split()
                # if len(words) < 9:
                #     logger.info(f'Skipping message {event.id} due to insufficient word count')
                #     return
                # If the word count is sufficient, process the message
                post = Post(
                    post_id=event.id,
                    channel_id=event.peer_id.channel_id,
                    rubric_id=None,
                    title=event.text[:50] if event.text else "No title",
                    content=event.text,
                    post_date=event.date.astimezone(pytz.utc).replace(tzinfo=None) + datetime.timedelta(hours=3)
                )
                try:
                    logger.debug(f'Attempting to add post {post.post_id} to database')
                    await add_post_async(post)
                    logger.info(f"Added post {post.post_id} from channel {post.channel_id}")
                except IntegrityError as e:
                    logger.warning(f"Failed to add post due to IntegrityError: {e}")
                    return

    while True:
        try:
            await client.connect()
            logger.debug(f'Connected Telegram client for account {account.account_id}')
            logger.info(f'Start listening for account {account.account_id}')

            # Start the connection checker
            asyncio.create_task(check_connection(client))

            await client.run_until_disconnected()
            logger.debug(f'Disconnected client for account {account.account_id}')
            break  # If we reach here, the disconnection was planned, so we exit the loop
        except Exception as e:
            logger.error(f'Error occurred: {e}. Retrying in 5 seconds.')
            await asyncio.sleep(5)  # Wait for 5 seconds before retrying


async def check_connection(client):
    while True:
        try:
            me = await client.get_me()
            logger.info(f'Current user: {me.username}')
        except Exception as e:
            logger.error(f'Error occurred during connection check: {e}. Retrying connection in 5 seconds.')
            await client.connect()
        await asyncio.sleep(60)  # Check the connection every 10 seconds


async def main():
    logger.info(f'Collect news service run')
    logger.debug(f'Getting accounts for channels')
    await asyncio.sleep(30)
    accounts = await get_all_accounts_from_db_async()
    logger.debug(f'Received {len(accounts)} accounts for channels')
    tasks = [listen_to_account(account) for account in accounts]
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
