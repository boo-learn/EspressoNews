import asyncio
from aio_pika import connect_robust, Message
from celery import shared_task


async def collect_news_async():
    connection = await connect_robust()
    channel = await connection.channel()

    await channel.declare_queue('news_collection_queue', durable=True)
    message = Message(body='collect_news'.encode())
    await channel.default_exchange.publish(message, routing_key='news_collection_queue')

    await connection.close()


@shared_task
def collect_news():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(collect_news_async())
