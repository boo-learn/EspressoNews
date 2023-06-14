
from aiogram import types

from bot_app.data.messages import gen_error_mess
from bot_app.loader import dp


@dp.message_handler()
async def cmd_help(message: types.Message):
    await message.answer(gen_error_mess())
