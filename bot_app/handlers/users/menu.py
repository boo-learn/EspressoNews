import re

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command

from bot_app.data.messages import gen_menu_mess
from bot_app.keyboards.default import kb_menu, get_kb_settings
from bot_app.keyboards.inlines import ikb_help
from bot_app.loader import dp
from bot_app.logic import ChannelLogicHandler


@dp.message_handler(Command('menu'))
async def cmd_menu(message: types.Message, state: FSMContext):
    await message.delete()
    await message.answer(gen_menu_mess(), reply_markup=kb_menu)


@dp.message_handler(regexp=re.compile(r'^Мои каналы$', re.IGNORECASE))
async def menu_button_my_channels(message: types.Message):
    logic_handler = ChannelLogicHandler()
    await logic_handler.send_channels_list_to_user(message)


@dp.message_handler(regexp=re.compile(r'^Настройки$', re.IGNORECASE))
async def menu_button_my_channels(message: types.Message):
    await message.answer('Список настроек', reply_markup=get_kb_settings())


@dp.message_handler(regexp=re.compile(r'^Донат$', re.IGNORECASE))
async def menu_button_my_channels(message: types.Message):
    await message.answer('Перевод на карту:')
    await message.answer('<b>1111 2222 3333 4444</b>')


@dp.message_handler(regexp=re.compile(r'^Помощь$', re.IGNORECASE))
async def menu_button_my_channels(message: types.Message):
    await message.answer('Частые вопросы', reply_markup=ikb_help)
