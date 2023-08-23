import asyncio
import logging

import aiogram
from aiogram.types import InlineKeyboardMarkup

from bot_app.data.messages import gen_digest_not_exist_mess, gen_digest_load_more
from bot_app.databases.cruds import DigestCRUD, UserCRUD
from bot_app.keyboards.inlines import ikb_load_more
from bot_app.loader import bot
from bot_app.logic.digest_logic_handler import DigestLogicHandler
from shared.config import RABBIT_HOST, DIGESTS_LIMIT, RETRY_LIMIT
from shared.loggers import get_logger
from shared.rabbitmq import Subscriber, QueuesType

logger = get_logger('bot.mailing')


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
    digest_summary_list, total_count = await logic_handler.fetch_and_format_digest(data["digest_id"], data['user_id'])

    # Combine all digest summaries into a nicely formatted string
    digest_message = '\n\n'.join(digest_summary_list)

    if total_count > DIGESTS_LIMIT:
        # Add the load more message to the digest message
        digest_message += '\n\n' + gen_digest_load_more()
        reply_markup = ikb_load_more(data["digest_id"], DIGESTS_LIMIT)
    else:
        reply_markup = None

    # Send the digest message in parts, if necessary
    try:
        await logic_handler.send_message_parts(
            send_method=lambda text, reply_markup=None: bot.send_message(
                chat_id=data["user_id"],
                text=text,
                disable_web_page_preview=True,
                reply_markup=reply_markup
            ),
            text=digest_message,
            max_length=4096,  # or any desired max_length
            reply_markup=reply_markup
        )
    except aiogram.exceptions.BotBlocked:
        # Here the user blocked the bot, so we disable him/her.
        await disable_user(data["user_id"])
    else:
        digest_crud = DigestCRUD()
        digest = await digest_crud.repository.get(data["digest_id"])
        await digest_crud.repository.change_digest(digest, data["user_id"])



async def no_digest(data):
    logger.info(f'Digest data {data}')
    try:
        await bot.send_message(chat_id=data["user_id"], text=gen_digest_not_exist_mess())
    except aiogram.exceptions.BotBlocked:
        # Here the user blocked the bot, so we disable him/her.
        await disable_user(data["user_id"])


async def disable_user(user_id: int):
    user_crud = UserCRUD()
    await user_crud.disable_user(user_id)
