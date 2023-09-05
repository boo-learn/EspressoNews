import logging

from aiogram import types
from aiogram.types import CallbackQuery
from bot_app.loader import dp
from bot_app.core.tools.handler_tools import HandlersTools

logger = logging.getLogger(__name__)


class StartHandlers(HandlersTools):
    def __init__(self):
        super().__init__()
        self.register_routes()

    def register_routes(self):
        self.aiogram_registrar.simply_handler_registration(
            dp.register_message_handler,
            self.start_command,
            'start',
            'command'
        )
        self.aiogram_registrar.simply_handler_registration(
            dp.register_callback_query_handler,
            self.action_after_start_btn,
            "Погнали!",
            'text'
        )
        self.aiogram_registrar.simply_handler_registration(
            dp.register_callback_query_handler,
            self.return_action,
            'return',
            'text'
        )

    async def start_command(self, message: types.Message):
        await self.aiogram_message_manager.send_message('start', first_name=message.from_user.first_name)

    async def action_after_start_btn(self, call: CallbackQuery):
        message_obj = call.message

        await self.aiogram_message_manager.delete_before_message()
        await message_obj.delete()
        await self.aiogram_message_manager.send_message('manual')

        await self.aiogram_message_manager.send_message(
            'after_start_btn',
            first_name=call.from_user.first_name
        )
        logger.debug('Message after start button sent')

    async def return_action(self, call: CallbackQuery):
        message_obj = call.message
        await self.aiogram_message_manager.delete_before_message()
        await message_obj.delete()
        await self.aiogram_message_manager.send_message('return')
