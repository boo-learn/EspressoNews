import asyncio
import datetime
import logging

from telethon import TelegramClient
from telethon.errors import SessionRevokedError
from telethon.sessions import StringSession

from shared.db_utils import (
    remove_account_from_db_async,
    get_first_active_account_from_db_async
)
from db_utils import add_post_async, get_subscribed_channels
from shared.models import Post
from shared.rabbitmq import Subscriber, QueuesType
from shared.config import RABBIT_HOST

# восстановить или переписать функцию get_subscribed_channels

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def collect_news():
    logger.info(f'START COLLECT NEWS')
    loaded_account = await get_first_active_account_from_db_async()

    if loaded_account:
        loaded_client = TelegramClient(StringSession(loaded_account.session_string), loaded_account.api_id,
                                       loaded_account.api_hash)
        await loaded_client.connect()

        try:
            subscribed_channels = await get_subscribed_channels(loaded_client)
            logger.info(f'get subscribed channels with teleton')

            for channel in subscribed_channels:
                logger.info(f'channel {channel.channel_id}')

            # Gather news from the last hour
            one_hour_ago = datetime.datetime.now() - datetime.timedelta(hours=1)
            logger.info(f"date one hour ago {one_hour_ago}")
            news = []

            for channel in subscribed_channels:
                logger.info(f"Subscribe channel {channel}")
                async for message in loaded_client.iter_messages(channel, limit=None, offset_date=one_hour_ago):
                    logger.info(f"News {message}")
                    news.append(message)

            logger.info(f"News from the last hour: {len(news)} messages")
            for message in news:
                print(f"{message.date}: {message.text}")

                # Save the message as a post in the database
                post = Post(
                    channel_id=message.peer_id.channel_id,
                    rubric_id=None,
                    title=message.text[:50],  # Use the first 50 characters of the message as the title
                    content=message.text,
                    summary=None,  # You can add a summary if needed
                    post_date=message.date
                )
                await add_post_async(post)

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
