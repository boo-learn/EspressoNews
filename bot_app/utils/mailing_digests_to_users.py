import asyncio
import logging

from aiogram.types import InlineKeyboardMarkup

from bot_app.data.messages import gen_digest_not_exist_mess, gen_digest_load_more
from bot_app.databases.cruds import DigestCRUD
from bot_app.keyboards.inlines import ikb_load_more
from bot_app.loader import bot
from bot_app.logic.digest_logic_handler import DigestLogicHandler
from shared.config import RABBIT_HOST, DIGESTS_LIMIT
from shared.rabbitmq import Subscriber, QueuesType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def mailing_digests_to_users():
    logger.info(f'Start digest mailing')
    subscriber = Subscriber(host=RABBIT_HOST, queue=QueuesType.bot_service)
    subscriber.subscribe("send_digest", send_digest)
    subscriber.subscribe("no_digest", no_digest)
    await subscriber.run()


async def send_digest(data: dict):
    logger.info(f'Digest trying send')
    logger.info(f'Digest data {data}')

    logic_handler = DigestLogicHandler()
    digest_summary_list, total_count = await logic_handler.fetch_and_format_digest(data["digest_id"])

    for digest_summary in digest_summary_list[:DIGESTS_LIMIT]:
        await logic_handler.send_message_parts(
            lambda text: bot.send_message(chat_id=data["user_id"], text=text),
            digest_summary
        )

    logger.info(f'Digest count {len(digest_summary_list)}, total count {DIGESTS_LIMIT}')
    if total_count > DIGESTS_LIMIT:
        await logic_handler.send_load_more(
            lambda text, reply_markup: bot.send_message(chat_id=data["user_id"], text=text, reply_markup=reply_markup),
            total_count,
            data["digest_id"],
            DIGESTS_LIMIT
        )


async def no_digest(data):
    logger.info(f'Digest data {data}')
    await bot.send_message(chat_id=data["user_id"], text=gen_digest_not_exist_mess())
