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


@celery_app.task(name='tasks.generate_all_digests_for_users', queue='digest_queue')
def generate_all_digests_for_users():
    logger.info("Task try to start")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_users_and_send_in_digest_service())


async def get_users_and_send_in_digest_service():
    logger.info("Task started")

    logger.info("Getting users from database...")
    async with async_session() as session:
        stmt = select(User)
        result = await session.execute(stmt)
        users = result.scalars().all()
    logger.info(f"Got users {users}")

    logger.info("Setting up RabbitMQ producer...")
    producer = Producer(host=RABBIT_HOST, queue=QueuesType.digest_service)

    logger.info("Sending messages to RabbitMQ...")
    for user in users:
        message: MessageData = {
            "type": 'prepare_digest',
            "data": user.user_id,
        }
        await producer.send_message(message, QueuesType.digest_service)
    logger.info("Messages sent to RabbitMQ")

    logger.info("Task finished")
