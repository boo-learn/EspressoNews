import asyncio
from telethon import TelegramClient
from aio_pika import connect, IncomingMessage
from shared.models import User, Subscription, Channel, Post
from shared.database import SessionLocal


async def collect_news(user: User, subscription: Subscription):
    async with TelegramClient(user.phone_number, user.api_id, user.api_hash) as client:
        channel = subscription.channel
        async for message in client.iter_messages(channel.channel_username, limit=100):
            if message.date > subscription.subscription_date:
                post = Post(
                    channel_id=channel.channel_id,
                    title=message.text,
                    content=message.message,
                    post_url=f"https://t.me/{channel.channel_username}/{message.id}",
                    post_date=message.date
                )
                session = SessionLocal()
                session.add(post)
                session.commit()


async def on_message(message: IncomingMessage):
    async with message.process():
        user_id = int(message.body.decode())
        session = SessionLocal()
        user = session.query(User).filter_by(id=user_id).first()
        if user:
            for subscription in user.subscriptions:
                if subscription.is_active:
                    await collect_news(user, subscription)


async def main():
    connection = await connect("amqp://guest:guest@localhost/")
    channel = await connection.channel()
    queue = await channel.declare_queue("news_collection_queue", durable=True)
    await queue.consume(on_message)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    finally:
        loop.close()
