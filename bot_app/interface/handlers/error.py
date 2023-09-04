import logging

from aiogram import types

from bot_app.loader import dp
from bot_app.core.tools.handler_tools import HandlersTools

logger = logging.getLogger(__name__)


class ErrorsHandlers(HandlersTools):
    def __init__(self):
        super().__init__()
        self.register_handlers()

    def register_handlers(self):
        self.registrar.simply_handler_registration(
            dp.register_message_handler,
            self.error,
            None,
            "always"
        )

    async def error(self, message: types.Message):
        await self.message_manager.send_message('error')
