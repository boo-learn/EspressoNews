import re

from aiogram import types
from aiogram.dispatcher.filters import Command

from bot_app.data.messages import gen_menu_mess
from bot_app.keyboards.default import kb_menu
from bot_app.keyboards.inlines import ikb_my_channels
from bot_app.loader import dp
from bot_app.utils import delete_previus_message_for_default


@dp.message_handler(Command('menu'))
async def cmd_menu(message: types.Message):
    await message.delete()
    await message.answer(gen_menu_mess(), reply_markup=kb_menu)


@dp.message_handler(regexp=re.compile(r'^Мои каналы$', re.IGNORECASE))
async def menu_button_my_channels(message: types.Message):
    await message.answer(text='Список каналов:', reply_markup=ikb_my_channels)


@dp.message_handler(regexp=re.compile(r'^Настройки$', re.IGNORECASE))
async def menu_button_my_channels(message: types.Message):
    await message.answer('Список настроек')


@dp.message_handler(regexp=re.compile(r'^Подписка$', re.IGNORECASE))
async def menu_button_my_channels(message: types.Message):
    await message.answer('Вы подписаны:')


@dp.message_handler(regexp=re.compile(r'^Помощь$', re.IGNORECASE))
async def menu_button_my_channels(message: types.Message):
    await message.answer('Вот и помощь')
