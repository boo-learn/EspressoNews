import logging

from aiogram import types

from bot_app.data.messages import gen_error_mess
from bot_app.loader import dp

logger = logging.getLogger(__name__)


@dp.message_handler()
async def cmd_help(message: types.Message):
    await message.answer(gen_error_mess())


# @dp.callback_query_handler()
# async def log_all_callback_queries(query: types.CallbackQuery):
#     logger.info(f'Received callback query: {query.data}')
