from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.types import CallbackQuery

from bot_app.data.messages import gen_start_mess, gen_mess_after_start_btn, gen_manual_mess
from bot_app.keyboards.inlines import ikb_start, get_posts_rubrics
from bot_app.loader import dp
from bot_app.utils import delete_previus_message_for_feedback


@dp.message_handler(Command('start'))
async def cmd_start(message: types.Message):
    await message.answer(gen_start_mess(message.from_user.first_name), reply_markup=ikb_start)


@dp.callback_query_handler(text='Погнали!')
async def action_after_start_btn(call: CallbackQuery):
    await delete_previus_message_for_feedback(call)
    await call.message.delete()
    await call.message.answer(gen_manual_mess())

    await call.message.answer(
        gen_mess_after_start_btn(call.from_user.first_name),
        reply_markup=get_posts_rubrics()
    )
