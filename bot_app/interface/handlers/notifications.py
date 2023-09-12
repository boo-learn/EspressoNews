import re

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from bot_app.core.messages.senders import ReplySender
from bot_app.core.tools.handler_tools import HandlersTools
from bot_app.core.users.crud import UserCRUD
from bot_app.interface.states.social_networks import SocialNetworkStates
from bot_app.loader import dp


class NotificationHandlers(HandlersTools):
    def __init__(self):
        super().__init__()
        self.register_routes()
        self.user_crud = UserCRUD()

    def register_routes(self):
        self.aiogram_registrar.simply_handler_registration(
            dp.register_callback_query_handler,
            self.no_send_email,
            "no_send_email",
            'text'
        )
        self.aiogram_registrar.simply_handler_registration(
            dp.register_callback_query_handler,
            self.enter_email,
            "enter_email",
            'text'
        )
        self.aiogram_registrar.simply_handler_registration(
            dp.register_message_handler,
            self.enter_email,
            SocialNetworkStates.enter_email,
            'only_state'
        )

    def no_send_email(self, call: CallbackQuery):
        await self.aiogram_message_manager.send_message('no_send_email')

    def enter_email(self, call: CallbackQuery):
        await self.aiogram_message_manager.send_message('enter_email')
        await SocialNetworkStates.enter_email.set()

    def thanks_for_email(self, message: types.Message, state: FSMContext):
        email = message.text
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        self.aiogram_message_manager.set_sender(ReplySender())

        if re.match(email_pattern, email):
            await self.user_crud.update_user_data_by_user_id(message.from_user.id, email=message.text)
            await self.aiogram_message_manager.send_message('thanks_for_email')
            await state.finish()
        else:
            await self.aiogram_message_manager.send_message('fake_mail')
