import asyncio
import datetime
import logging

import pytz
from telethon import TelegramClient
from telethon.errors import SessionRevokedError
from telethon.sessions import StringSession
from sqlalchemy.exc import IntegrityError
from shared.db_utils import (
    remove_account_from_db_async,
    get_first_active_account_from_db_async
)
from db_utils import add_post_async, get_subscribed_channels
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


async def collect_news():
    logger.info(f'START COLLECT NEWS')
    loaded_account = await get_first_active_account_from_db_async()

    if loaded_account:
        loaded_client = TelegramClient(StringSession(loaded_account.session_string), loaded_account.api_id,
                                       loaded_account.api_hash)
        await loaded_client.connect()
        logger.info(f'Try connect to telegram client')

        try:
            logger.info(f'Connected to telegram client')
            subscribed_channels = await get_subscribed_channels(loaded_client)
            logger.info(f'Get subscribed channels with teleton {subscribed_channels}')

            # Gather news from the last hour
            one_hour_ago = datetime.datetime.now(pytz.timezone('UTC')) - datetime.timedelta(hours=100)
            one_hour_ago = one_hour_ago.astimezone(pytz.timezone('Etc/GMT-3'))  # convert to UTC+3
            logger.info(f"date one hour ago {one_hour_ago}")
            news = []

            for channel in subscribed_channels:
                logger.info(f"Subscribe channel {channel.username}, id {channel.id}")
                async for message in loaded_client.iter_messages(channel, limit=None):
                    if message.date < one_hour_ago:
                        break
                    logger.debug(f"News {message}")
                    # Проверяем, совпадает ли channel_id с channel_id текущего канала
                    if message.peer_id.channel_id == channel.id:
                        # Проверяем, что количество слов в сообщении не менее 45
                        if message.text and len(message.text.split()) >= 45:
                            news.append(message)
                        else:
                            logger.info(
                                f"Skipping message {message.id} from channel {message.peer_id.channel_id} due to insufficient word count.")
                    else:
                        logger.info(f"Skipping message {message.id} from channel {message.peer_id.channel_id}")

            logger.info(f"News from the last hour: {len(news)} messages")
            for message in news:
                # If message.text is empty, skip this iteration
                if not message.text:
                    continue

                # Save the message as a post in the database
                post = Post(
                    post_id=message.id,
                    channel_id=message.peer_id.channel_id,
                    rubric_id=None,
                    title=message.text[:50] if message.text else "No title",
                    content=message.text if message.text else " ",
                    summary=None,  # You can add a summary if needed
                    post_date=message.date.astimezone(pytz.utc).replace(tzinfo=None) + datetime.timedelta(hours=3)
                    # Make the datetime timezone unaware
                )
                try:
                    await add_post_async(post)
                except IntegrityError as e:
                    logger.warning(f"Failed to add post due to IntegrityError: {e}")
                    continue

            message: MessageData = {
                "type": 'summarize_news',
                "data": None
            }

            producer = Producer(host=RABBIT_HOST, queue=QueuesType.summary_service)
            await producer.send_message(message, QueuesType.summary_service)
        except SessionRevokedError:
            logger.info(f"The session has been revoked by the user.")
            await remove_account_from_db_async(loaded_account.account_id)

        await loaded_client.disconnect()
    else:
        logger.info(f"Account not found.")


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
