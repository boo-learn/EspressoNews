import asyncio
from celery import shared_task

from shared.rabbitmq import Producer, QueuesType, MessageData
from shared.config import RABBIT_HOST


async def summarize_news_async():
    producer = Producer(host=RABBIT_HOST)
    message: MessageData = {
        "type": "summarize_news",
        "data": None
    }
    await producer.send_message(message_with_data=message, queue=QueuesType.summary_service)


@shared_task
def summarize_news():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(summarize_news_async())
