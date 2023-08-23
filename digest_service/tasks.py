import asyncio
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from shared.database import async_session
from shared.celery_app import celery_app
from shared.database import async_session
from shared.models import User, Digest
from shared.rabbitmq import Producer, QueuesType, MessageData
from shared.config import RABBIT_HOST
from shared.loggers import get_logger


logger = get_logger('digest-mon.tasks')


@celery_app.task(name='tasks.generate_digest_for_user', queue='digest_queue')
def generate_digest_for_user(user_id):
    logger.info("Task try to start")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_user_and_send_in_digest_service(user_id))


async def get_user_and_send_in_digest_service(user_id):
    logger.info("Task started")
    async with async_session() as session:
        digest_result = await session.execute(
            select(Digest).filter(
                Digest.user_id == user_id,
                Digest.is_active == True
            ).options(
                joinedload(Digest.digest_recs)
            )
        )

        digest = digest_result.unique().scalar_one_or_none()
        if digest is None or len(digest.digest_ids) == 0:
            producer = Producer(host=RABBIT_HOST, queue=QueuesType.bot_service)
            logger.info(f"no digest")
            message: MessageData = {
                "type": "no_digest",
                "data": {
                    "user_id": user_id
                }
            }
            await producer.send_message(message_with_data=message, queue=QueuesType.bot_service)
        else:
            producer = Producer(host=RABBIT_HOST, queue=QueuesType.bot_service)
            logger.info(f"send_digest")
            message: MessageData = {
                "type": "send_digest",  # send_digest
                "data": {
                    "user_id": user_id,
                    "digest_id": digest.id,
                }
            }
            await producer.send_message(message_with_data=message, queue=QueuesType.bot_service)
