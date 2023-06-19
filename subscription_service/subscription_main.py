import json
import asyncio
from aio_pika import connect, IncomingMessage
from tasks import subscribe_task, unsubscribe_task
from shared.db_utils import (get_first_active_account_from_db_async, get_subscribed_channels,
                             get_unique_channel_ids_async, remove_account_from_db_async)
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionRevokedError
from shared.rabbitmq import Subscriber, QueuesType
from shared.config import RABBIT_HOST


async def check_subscriptions():
    loaded_account = await get_first_active_account_from_db_async()

    if loaded_account:
        loaded_client = TelegramClient(StringSession(loaded_account.session_string), loaded_account.api_id,
                                       loaded_account.api_hash)
        await loaded_client.connect()

        try:
            subscribed_channels = await get_subscribed_channels(loaded_client)
            print("Bot is subscribed to the following channels:")

            channels_to_subscribe = []
            channels_to_unsubscribe = []

            for channel in subscribed_channels:
                needed_unique_channel_ids = await get_unique_channel_ids_async()
                print(channel.channel_id)

                if channel.channel_id not in needed_unique_channel_ids:
                    channels_to_unsubscribe.append(channel.username)
                else:
                    channels_to_subscribe.append(channel.username)

            print("Channels to subscribe:", channels_to_subscribe)
            print("Channels to unsubscribe:", channels_to_unsubscribe)

            for channel_username in channels_to_subscribe:
                subscribe_task.apply_async(args=(loaded_account.account_id, channel_username))

            for channel_username in channels_to_unsubscribe:
                unsubscribe_task.apply_async(args=(loaded_account.account_id, channel_username))

        except SessionRevokedError:
            print("The session has been revoked by the user.")
            await remove_account_from_db_async(loaded_account.account_id)

        await loaded_client.disconnect()
    else:
        print("Account not found")


async def main():
    subscriber = Subscriber(host=RABBIT_HOST, queue=QueuesType.news_collection_service)
    subscriber.subscribe("subscribe", check_subscriptions)
    subscriber.subscribe("unsubscribe", check_subscriptions)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    finally:
        loop.close()
