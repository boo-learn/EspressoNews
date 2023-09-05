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
        self.aiogram_registrar.multilingual_handler_registration(
            dp.register_message_handler,
            self.menu_button_my_channels,
            'regexp_my_channels',
            'regexp'
        )
        self.aiogram_registrar.multilingual_handler_registration(
            dp.register_message_handler,
            self.menu_button_settings,
            'regexp_settings',
            'regexp'
        )
        self.aiogram_registrar.multilingual_handler_registration(
            dp.register_message_handler,
            self.menu_button_donate,
            'regexp_donat',
            'regexp'
        )
        self.aiogram_registrar.multilingual_handler_registration(
            dp.register_message_handler,
            self.menu_button_help,
            'regexp_help',
            'regexp'
        )

    async def cmd_menu(self, message: types.Message):
        await message.delete()
        logger.info(
            f'14 шаг - проверка handler menu подходим к отрпавке сообщения'
        )
        await self.aiogram_message_manager.send_message('menu')

    async def menu_button_my_channels(self, message: types.Message):
        user_id = message.from_user.id
        logic_handler = ChannelLogicHandler()
        await logic_handler.send_channels_list_to_user(
            self.aiogram_message_manager,
            user_id
        )

    async def menu_button_settings(self, message: types.Message):
        await self.aiogram_message_manager.send_message('settings')

    async def menu_button_donate(self, message: types.Message):
        await self.aiogram_message_manager.send_message('thank_you')

    async def menu_button_help(self, message: types.Message):
        await self.aiogram_message_manager.send_message('frequent_questions')
