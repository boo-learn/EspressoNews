import asyncio
import logging

from celery import shared_task

from shared.celery_app import celery_app
from shared.rabbitmq import Producer, QueuesType, MessageData
from shared.loggers import get_logger
from shared.config import RABBIT_HOST

logger = get_logger('collector.tasks')


async def send_to_subscribe_channel(type: str, msg: str):
    message: MessageData = {
        "type": type,
        "data": msg
    }
    producer = Producer(host=RABBIT_HOST, queue=QueuesType.subscription_service)
    await producer.send_message(message, QueuesType.subscription_service)
