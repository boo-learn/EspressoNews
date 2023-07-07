import logging
import json
import asyncio
from aio_pika import connect, IncomingMessage
from tasks import subscribe_task, unsubscribe_task
from shared.db_utils import (
    get_first_active_account_from_db_async,
    get_usernames_subscribed_channels,
    get_unique_channel_usernames,
    remove_account_from_db_async
)
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionRevokedError
from shared.rabbitmq import Subscriber, QueuesType
from shared.config import RABBIT_HOST

# Configuring logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)


async def check_subscriptions():
    loaded_account = await get_first_active_account_from_db_async()

    if loaded_account:
        loaded_client = TelegramClient(StringSession(loaded_account.session_string), loaded_account.api_id,
                                       loaded_account.api_hash)
        await loaded_client.connect()

        try:
            # Получаем список username'ов фактически подписанных каналов
            usernames_subscribed_channels = await get_usernames_subscribed_channels(loaded_client)
            logger.info(f"Список username'ов фактически подписанных каналов: {usernames_subscribed_channels}")

            # Получаем список каналов, на которые бот должен быть подписан
            needed_unique_channel_usernames = await get_unique_channel_usernames()

            # Подготавливаем списки для подписки и отписки
            channels_to_subscribe = []
            channels_to_unsubscribe = []

            logger.info(
                f'Список sername\'ов, на которые нужно подписаться (не отфильтрованный): '
                f'{needed_unique_channel_usernames}'
            )
            logger.info(f'UNSUBSCRIBE CHANNELS ID\'S ARRAY: {channels_to_unsubscribe}')

            # Определяем каналы для подписки и отписки
            for needed_username in needed_unique_channel_usernames:
                if needed_username not in usernames_subscribed_channels:
                    channels_to_subscribe.append(needed_username)
            for subscribed_username in usernames_subscribed_channels:
                if subscribed_username not in needed_unique_channel_usernames:
                    channels_to_unsubscribe.append(subscribed_username)

            logger.info(f"Channels to subscribe: {channels_to_subscribe}")
            logger.info(f"Channels to unsubscribe: {channels_to_unsubscribe}")

            for channel_username in channels_to_subscribe:
                subscribe_task.apply_async(args=[loaded_account.account_id, channel_username])

            for channel_username in channels_to_unsubscribe:
                unsubscribe_task.apply_async(args=[loaded_account.account_id, channel_username])

        except SessionRevokedError:
            logger.error("The session has been revoked by the user.")
            await remove_account_from_db_async(loaded_account.account_id)

        await loaded_client.disconnect()
    else:
        logger.warning("Account not found")


async def main():
    logger.info("Starting main function...")
    subscriber = Subscriber(host=RABBIT_HOST, queue=QueuesType.subscription_service)
    subscriber.subscribe("subscribe", check_subscriptions)
    subscriber.subscribe("unsubscribe", check_subscriptions)
    logger.info("Main function has been started...")
    await subscriber.run()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.create_task(main())
        loop.run_forever()
    finally:
        logger.info("Closing the event loop...")
        loop.close()
