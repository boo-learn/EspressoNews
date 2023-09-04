import logging

from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware

from bot_app.core.users.crud import UserCRUD
from bot_app.digests.cruds import DigestCRUD
from bot_app.digests.enter_controllers import DigestMailingManager
from bot_app.loader import dp
from bot_app.core.messages.manager import MessageManager

logger = logging.getLogger(__name__)


class RegistrarMiddleware(BaseMiddleware):
    """
    Middleware for updating message data and registering default bot commands.

    Attributes:
        handlers (list): List of handlers for processing incoming messages.
        user_crud (UserCRUD): CRUD operations for users.
        mailing_manager (DigestMailingManager): Handles digest mailing.
        digest_crud (DigestCRUD): CRUD operations for digests.
    """

    def __init__(self, handlers: list):
        """
        Initializes the Registrar middleware with the provided handlers and required dependencies.

        :param handlers: List of handlers for processing incoming messages.
        """
        self.handlers = handlers
        self.user_crud = UserCRUD()
        self.digest_crud = DigestCRUD()
        self.mailing_manager = DigestMailingManager()
        super(RegistrarMiddleware, self).__init__()

    async def on_pre_process_message(self, message: types.Message, data: dict) -> None:
        """
        Invokes the update method to modify the incoming message and registers default bot commands.

        :param message: The incoming message.
        :param data: Additional data related to the message.
        """
        user = await self.registration_user(message)
        user_lang_code = user.settings.language.code

        self.update_handlers_message_manager(message, user_lang_code)
        await self.registration_translate_default_commands(user_lang_code)

    def update_handlers_message_manager(
            self,
            message: types.Message,
            language: str = 'en'
    ) -> None:
        """
        Updates the message based on the provided handlers.

        :param message: Aiogram message object.
        :param language: User language for user's messages.
        """
        for handler_class in self.handlers:
            handler_class.update_language(language)
            handler_class.update_message(message)

    async def registration_user(self, message: types.Message):
        user = await self.user_crud.check_user_and_create_if_none(
            message.from_user.id,
            message.from_user.username,
            message.from_user.first_name,
            message.from_user.last_name,
        )

        if not user.is_active:
            await self.user_crud.enable_user(user)
            await self.digest_crud.repository.create(
                user_id=message.from_user.id
            )

            periodicity_option = await self.user_crud.get_settings_option_for_user(
                message.from_user.id,
                'periodicity'
            )

            await self.mailing_manager.create_rule(message.from_user.id, periodicity_option)

        return user

    @staticmethod
    async def registration_translate_default_commands(language: str) -> None:
        """
        Registers default bot commands with the bot.

        :param language: User language for user's messages.
        """
        cmd_keys = [
            'desc_cmd_menu',
            'desc_cmd_help'
        ]

        message_manager = MessageManager()
        message_manager.set_language(language)

        await dp.bot.set_my_commands([
            types.BotCommand(
                '/' + key.split('desc_cmd_')[-1],
                message_manager.get_message(key)
            ) for key in cmd_keys
        ])
