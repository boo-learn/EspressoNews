from aiogram import types
from aiogram.dispatcher.filters import Command

from bot_app.data.messages import gen_help_mess
from bot_app.loader import dp


@dp.message_handler(Command('help'))
async def cmd_help(message: types.Message):
    await message.answer(gen_help_mess(message.from_user.first_name))
