import asyncio
import logging
from sqlalchemy import select

from shared.celery_app import celery_app
from shared.database import async_session
from shared.models import User
from shared.rabbitmq import Producer, QueuesType, MessageData
from shared.config import RABBIT_HOST

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@celery_app.task(name='tasks.generate_digest_for_user', queue='digest_queue')
def generate_digest_for_user(user_id):
    logger.info("Task try to start")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_user_and_send_in_digest_service(user_id))


async def get_user_and_send_in_digest_service(user_id):
    logger.info("Task started")

    logger.info("Getting users from database...")

    logger.info("Setting up RabbitMQ producer...")
    producer = Producer(host=RABBIT_HOST, queue=QueuesType.digest_service)

    logger.info("Sending messages to RabbitMQ...")
    message: MessageData = {
        "type": 'prepare_digest',
        "data": user_id,
    }
    await producer.send_message(message, QueuesType.digest_service)

    logger.info("Messages sent to RabbitMQ")
    logger.info("Task finished")
