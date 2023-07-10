import logging

from aiogram import Dispatcher

from bot_app.data.messages import gen_digest_not_exist_mess
from bot_app.databases.cruds import DigestCRUD
from shared.config import RABBIT_HOST
from shared.rabbitmq import Subscriber, QueuesType


async def mailing_digests_to_users(dp: Dispatcher):
    subscriber = Subscriber(host=RABBIT_HOST, queue=QueuesType.bot_service)

    async def send_digest(user_id, digest_id):
        digest_crud = DigestCRUD()
        digest_summary = await digest_crud.get_digest_summary_by_id(digest_id)

        await dp.bot.send_message(chat_id=user_id, text=digest_summary)

    async def digest_not_exist(user_id):
        await dp.bot.send_message(chat_id=user_id, text=gen_digest_not_exist_mess())

    await subscriber.run()
