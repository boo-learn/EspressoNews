import asyncio
from celery import shared_task

from shared.rabbitmq import Producer, QueuesType, MessageData
from shared.config import RABBIT_HOST


async def collect_news_async():
    # Пример отправки:
    producer = Producer(host=RABBIT_HOST)
    message: MessageData = {
        "type": "collect_news",
        "data": None
    }
    await producer.send_message(message_with_data=message, queue=QueuesType.news_collection_service)


@shared_task
def collect_news():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(collect_news_async())
