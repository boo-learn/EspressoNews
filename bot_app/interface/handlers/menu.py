import logging

from aiogram import types

from bot_app.loader import dp
from bot_app.channels.enter_controllers import ChannelLogicHandler
from bot_app.core.tools.handler_tools import HandlersTools


logger = logging.getLogger(__name__)


class MenuHandlers(HandlersTools):
    def __init__(self):
        super().__init__()
        self.register_routes()

    def register_routes(self):
        self.aiogram_registrar.simply_handler_registration(
            dp.register_message_handler,
            self.cmd_menu,
            'menu',
            'command'
        )

    async def cmd_menu(self, message: types.Message):
        await self.aiogram_message_manager.send_message('to_main_menu')
