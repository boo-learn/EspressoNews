import asyncio
import logging

from celery import shared_task

from shared.celery_app import celery_app
from shared.rabbitmq import Producer, QueuesType, MessageData
from shared.config import RABBIT_HOST

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def collect_news_async():
    producer = Producer(host=RABBIT_HOST, queue=QueuesType.news_collection_service)
    message: MessageData = {
        "type": "collect_news",
        "data": None
    }
    await producer.send_message(message_with_data=message, queue=QueuesType.news_collection_service)
    logger.info(f'RabbitMq go complete task')


@celery_app.task(name='tasks.collect_news', queue='news_collection_queue')
def collect_news():
    logger.info(f'Test task completed success')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(collect_news_async())

