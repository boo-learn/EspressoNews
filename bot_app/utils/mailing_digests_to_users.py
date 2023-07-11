import logging
from bot_app.data.messages import gen_digest_not_exist_mess
from bot_app.databases.cruds import DigestCRUD
from bot_app.loader import bot
from shared.config import RABBIT_HOST
from shared.rabbitmq import Subscriber, QueuesType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def mailing_digests_to_users():
    logger.info(f'Start digest mailing')
    subscriber = Subscriber(host=RABBIT_HOST, queue=QueuesType.bot_service)
    subscriber.subscribe("send_digest", send_digest)
    subscriber.subscribe("no_digest", no_digest)
    await subscriber.run()


async def send_digest(data):
    logger.info(f'Digest trying send')
    logger.info(f'Digest data {data}')
    digest_crud = DigestCRUD()
    digest_summary = await digest_crud.get_digest_summary_by_id(data["digest_id"])
    logger.info(f'Digest summary {digest_summary}')
    await bot.send_message(chat_id=data["user_id"], text=digest_summary)


async def no_digest(data):
    logger.info(f'Digest data {data}')
    await bot.send_message(chat_id=data["user_id"], text=gen_digest_not_exist_mess())
