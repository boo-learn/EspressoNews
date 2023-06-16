import asyncio
from celery import shared_task

from shared.rabbitmq import Producer, QueuesType
from shared.config import RABBIT_HOST


async def collect_news_async():
    producer = Producer(host=RABBIT_HOST)
    await producer.send_message(message='collect_news', queue=QueuesType.news_collection_service)
    await producer.close()


@shared_task
def collect_news():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(collect_news_async())
