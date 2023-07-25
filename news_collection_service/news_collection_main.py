import asyncio
import datetime
import logging

import pytz
from telethon import TelegramClient
from telethon.errors import SessionRevokedError
from telethon.sessions import StringSession
from sqlalchemy.exc import IntegrityError

from news_collection_service.tasks import send_to_subscribe_channel
from shared.db_utils import (
    remove_account_from_db_async,
    get_first_active_account_from_db_async, get_account_from_db_async
)
from db_utils import add_post_async, get_subscribed_channels, get_all_channels, get_channels_by_account_id
from shared.models import Post
from shared.rabbitmq import Subscriber, QueuesType, MessageData, Producer
from shared.config import RABBIT_HOST

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


async def get_accounts_for_channels(channels):
    accounts = []
    for channel in channels:
        if channel.account_id is not None:
            account = await get_account_from_db_async(channel.account_id)
            if account is not None:
                accounts.append(account)
    return accounts


async def collect_news():
    logger.info('START COLLECT NEWS')
    channels = await get_all_channels()
    accounts = await get_accounts_for_channels(channels)

    tasks = []
    for account in accounts:
        task = asyncio.create_task(collect_news_for_account(account))
        tasks.append(task)

    await asyncio.gather(*tasks)

    message: MessageData = {
        "type": 'summarize_news',
        "data": None
    }

    producer = Producer(host=RABBIT_HOST, queue=QueuesType.summary_service)
    await producer.send_message(message, QueuesType.summary_service)


async def collect_news_for_account(account):
    max_retry_attempts = 10
    retry_delay = 60  # Delay in seconds

    for attempt in range(max_retry_attempts):
        client = None
        try:
            logger.info(f'Start collecting news for account {account.account_id}')
            client = TelegramClient(StringSession(account.session_string), account.api_id, account.api_hash)

            await client.connect()
            logger.info('Connected to Telegram client')
            subscribed_channels = await get_subscribed_channels(client)
            logger.info(f'Get subscribed channels with Telethon {subscribed_channels}')

            half_hour_ago = datetime.datetime.now(pytz.timezone('UTC')) - datetime.timedelta(hours=50) # add 1 minute to avoid missing posts
            half_hour_ago = half_hour_ago.astimezone(pytz.timezone('Etc/GMT-3'))  # convert to UTC+3
            logger.info(f"Date ago {half_hour_ago}")

            news = []

            subscribed_channel_ids = {channel.id for channel in
                                      subscribed_channels}  # Create a set of subscribed channel IDs

            for channel in subscribed_channels:
                logger.info(f"Subscribe channel {channel.username}, id {channel.id}")
                async for message in client.iter_messages(channel, limit=None):
                    if message.date < half_hour_ago:
                        break
                    logger.debug(f"News {message}")
                    # Check if the message is from a subscribed channel
                    if message.peer_id.channel_id in subscribed_channel_ids:
                        if message.text and len(message.text.split()) >= 10:
                            news.append(message)
                        else:
                            logger.info(
                                f"Skipping message {message.id} from channel {message.peer_id.channel_id} due to insufficient word count.")
                    else:
                        logger.info(
                            f"Skipping message {message.id} from channel {message.peer_id.channel_id} as it is not a subscribed channel")

            logger.info(f"News from the last hour: {len(news)} messages")

            for message in news:
                if not message.text:
                    continue
                post = Post(
                    post_id=message.id,
                    channel_id=message.peer_id.channel_id,
                    rubric_id=None,
                    title=message.text[:50] if message.text else "No title",
                    content=message.text if message.text else " ",
                    post_date=message.date.astimezone(pytz.utc).replace(tzinfo=None) + datetime.timedelta(hours=3)
                )
                try:
                    await add_post_async(post)
                    logger.info(f"Added post {post.post_id} from channel {post.channel_id}")
                except IntegrityError as e:
                    logger.warning(f"Failed to add post due to IntegrityError: {e}")
                    continue

        except Exception as e:
            logger.info(
                f"Attempt {attempt + 1} failed. The session has been revoked by the user. Retrying in {retry_delay} seconds.")
            await asyncio.sleep(retry_delay)  # Wait for the delay before the next attempt
            continue

        finally:
            if client:
                await client.disconnect()

        break  # If the code execution reaches this point, no exceptions were thrown and the loop can be broken

    else:  # This block will execute if the loop has finished normally, meaning all attempts have failed
        logger.error(f"All {max_retry_attempts} attempts failed. Stop trying.")
        channels = await get_channels_by_account_id(account.account_id)
        await remove_account_from_db_async(account.account_id)
        for channel in channels:
            await send_to_subscribe_channel("subscribe", channel.channel_username)


async def main():
    logger.info(f'Collect news service run')
    subscriber = Subscriber(host=RABBIT_HOST, queue=QueuesType.news_collection_service)
    subscriber.subscribe(message_type="collect_news", callback=collect_news)
    logger.info(f'Subscriber up')
    await subscriber.run()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(collect_news())
        loop.create_task(main())
        loop.run_forever()
    finally:
        logger.info("Closing the event loop...")
        loop.close()
