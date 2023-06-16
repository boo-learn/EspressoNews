from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.types import CallbackQuery

from bot_app.data.messages import gen_help_mess, gen_answer_to_question_mess
from bot_app.loader import dp


@dp.message_handler(Command('help'))
async def cmd_help(message: types.Message):
    await message.answer(gen_help_mess(message.from_user.first_name))


@dp.callback_query_handler(text_contains='question_')
async def answers_to_the_questions(call: CallbackQuery):
    await call.message.answer(gen_answer_to_question_mess(call.data.split('_')[-1]))
