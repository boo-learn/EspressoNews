import logging

from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware
from bot_app.databases.cruds import UserCRUD, DigestCRUD
from bot_app.utils.create_mail_rules import create_mail_rule

logger = logging.getLogger(__name__)


class UserMiddleware(BaseMiddleware):

    async def on_pre_process_message(self, message: types.Message, data: dict):
        user_crud = UserCRUD()
        user_exist = await user_crud.is_user_exist(message.from_user.id)
        logger.info(f'Checking user {message.from_user.id}')
        if not user_exist:
            logger.info('User not exist, creating...')
            await user_crud.check_user_and_create_if_none(
                message.from_user.id,
                message.from_user.username,
                message.from_user.first_name,
                message.from_user.last_name,
            )
            user_crud = UserCRUD()
            digest_crud = DigestCRUD()
            await digest_crud.repository.create(
                user_id=message.from_user.id
            )
            periodicity_option = await user_crud.get_settings_option_for_user(message.from_user.id, 'periodicity')
            await create_mail_rule(message.from_user.id, periodicity_option)
        elif not user_exist.is_active:
            logger.info('User is not active, updating...')
            await user_crud.enable_user(message.from_user.id)

