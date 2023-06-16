import asyncio
import datetime

from aio_pika import connect, IncomingMessage
from telethon import TelegramClient
from telethon.errors import SessionRevokedError
from telethon.sessions import StringSession

from db_utils import get_subscribed_channels, \
    remove_account_from_db_async, get_first_active_account_from_db_async, add_post_async
from shared.models import Post


async def collect_news():
    loaded_account = await get_first_active_account_from_db_async()

    if loaded_account:
        loaded_client = TelegramClient(StringSession(loaded_account.session_string), loaded_account.api_id,
                                       loaded_account.api_hash)
        await loaded_client.connect()

        try:
            subscribed_channels = await get_subscribed_channels(loaded_client)
            print("Bot is subscribed to the following channels:")

            for channel in subscribed_channels:
                print(channel.channel_id)

            # Gather news from the last hour
            one_hour_ago = datetime.datetime.now() - datetime.timedelta(hours=1)
            news = []

            for channel in subscribed_channels:
                async for message in loaded_client.iter_messages(channel, limit=None, offset_date=one_hour_ago):
                    news.append(message)

            print(f"News from the last hour: {len(news)} messages")
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
            print("The session has been revoked by the user.")
            await remove_account_from_db_async(loaded_account.account_id)

        await loaded_client.disconnect()
    else:
        print("Account not found")


async def on_message(message: IncomingMessage):
    print("Received message:", message.body.decode())
    await message.ack()

    if message.body.decode() == "collect_news":
        await collect_news()


async def main():
    connection = await connect("amqp://guest:guest@localhost/")
    channel = await connection.channel()
    queue = await channel.declare_queue("news_queue", durable=True)
    await queue.consume(on_message)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    finally:
        loop.close()
