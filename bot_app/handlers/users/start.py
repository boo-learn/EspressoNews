import re

from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.types import CallbackQuery

from bot_app.data.messages import gen_start_mess, gen_mess_after_start_btn_1, gen_mess_after_start_btn_2, \
    gen_adding_own_channels, gen_adding_users_channels
from bot_app.keyboards.inlines import ikb_start, ikb_after_start, ikb_choose_category, ikb_back
from bot_app.loader import dp
from bot_app.utils import delete_previus_message_for_feedback


@dp.message_handler(Command('start'))
async def cmd_start(message: types.Message):
    await message.answer(gen_start_mess(message.from_user.first_name), reply_markup=ikb_start)


@dp.callback_query_handler(text='Погнали!')
async def action_after_start_btn(call: CallbackQuery):
    await delete_previus_message_for_feedback(call)
    await call.message.delete()
    await call.message.answer(gen_mess_after_start_btn_1(call.from_user.first_name))
    await call.message.answer(gen_mess_after_start_btn_2(), reply_markup=ikb_after_start)


@dp.callback_query_handler(text='adding first method')
async def action_after_start_btn(call: CallbackQuery):
    await delete_previus_message_for_feedback(call)
    await call.message.delete()
    await call.message.answer(gen_adding_users_channels(), reply_markup=ikb_choose_category)


@dp.callback_query_handler(text='adding second method')
async def action_after_start_btn(call: CallbackQuery):
    await delete_previus_message_for_feedback(call)
    await call.message.delete()
    await call.message.answer(gen_adding_own_channels(), reply_markup=ikb_back)






