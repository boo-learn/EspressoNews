import logging
import json
import asyncio
from aio_pika import connect, IncomingMessage
from tasks import subscribe_task
from shared.db_utils import (get_first_active_account_from_db_async, get_subscribed_channels,
                             get_unique_channel_ids_async, remove_account_from_db_async)
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionRevokedError
from shared.rabbitmq import Subscriber, QueuesType
from shared.config import RABBIT_HOST

# Configuring logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)


async def check_subscriptions(message_data):
    logger.info("I received a command.")
    loaded_account = await get_first_active_account_from_db_async()

    if loaded_account:
        logger.info("Found an active account. Starting a client...")
        loaded_client = TelegramClient(StringSession(loaded_account.session_string), loaded_account.api_id,
                                       loaded_account.api_hash)
        await loaded_client.connect()

        try:
            # Получаем список фактически подписанных каналов
            subscribed_channels = await get_subscribed_channels(loaded_client)
            logger.info(f"Bot is subscribed to the following channels: {subscribed_channels}")

            # Получаем список каналов, на которые бот должен быть подписан
            needed_unique_channel_ids = await get_unique_channel_ids_async()

            # Подготавливаем списки для подписки и отписки
            channels_to_subscribe = []
            channels_to_unsubscribe = []

            # Извлекаем ID каналов из подписанных каналов
            subscribed_channel_ids = [channel.channel_id for channel in subscribed_channels]

            # Определяем каналы для подписки и отписки
            for needed_id in needed_unique_channel_ids:
                if needed_id not in subscribed_channel_ids:
                    channels_to_subscribe.append(needed_id)
            for subscribed_id in subscribed_channel_ids:
                if subscribed_id not in needed_unique_channel_ids:
                    channels_to_unsubscribe.append(subscribed_id)

            logger.info(f"Channels to subscribe: {channels_to_subscribe}")
            logger.info(f"Channels to unsubscribe: {channels_to_unsubscribe}")

            for channel_username in channels_to_subscribe:
                subscribe_task.apply_async(args=[loaded_account.account_id, channel_username])

            # for channel_username in channels_to_unsubscribe:
            #     unsubscribe_task.delay(loaded_account.account_id, channel_username)

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
    # subscriber.subscribe("unsubscribe", check_subscriptions)
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
