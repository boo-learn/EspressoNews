import logging

from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.types import CallbackQuery

from bot_app.data.messages import gen_start_mess, gen_mess_after_start_btn, gen_manual_mess, gen_return_message
from bot_app.databases.cruds import UserCRUD
from bot_app.keyboards.inlines import ikb_start, get_posts_rubrics
from bot_app.loader import dp
from bot_app.utils import delete_previus_message_for_feedback
from bot_app.utils.create_mail_rules import create_mail_rule

logger = logging.getLogger(__name__)


@dp.message_handler(Command('start'))
async def cmd_start(message: types.Message):
    logger.debug('Received start command')
    user_crud = UserCRUD()
    await user_crud.check_user_and_create_if_none(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name,
        message.from_user.last_name,
    )
    await create_mail_rule(message.from_user.id)  # Add this line to call create_mail_rule
    logger.info('User checked and created if not existing')
    await message.answer(gen_start_mess(message.from_user.first_name))
    logger.debug('Start message sent')


@dp.callback_query_handler(text='Погнали!')
async def action_after_start_btn(call: CallbackQuery):
    logger.debug('Received Погнали! callback')
    await delete_previus_message_for_feedback(call)
    await call.message.delete()
    await call.message.answer(gen_manual_mess())
    logger.debug('Manual message sent')

    await call.message.answer(
        gen_mess_after_start_btn(call.from_user.first_name),
        reply_markup=get_posts_rubrics()
    )
    logger.debug('Message after start button sent')


@dp.callback_query_handler(text='return')
async def action_after_start_btn(call: CallbackQuery):
    logger.debug('Received return callback')
    await delete_previus_message_for_feedback(call)
    await call.message.delete()

    await call.message.answer(gen_return_message())
    logger.debug('Return message sent')
