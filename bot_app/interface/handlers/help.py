from aiogram import types
from aiogram.types import CallbackQuery

from bot_app.loader import dp
from bot_app.core.tools.handler_tools import HandlersTools


class HelpHandlers(HandlersTools):
    def __init__(self):
        super().__init__()
        self.register_handlers()

    def register_handlers(self):
        self.registrar.multilingual_handler_registration(
            aiogram_register_func=dp.register_message_handler,
            handler=self.help_main,
            pattern_or_list='kb_reply_help',
            handler_type='text'
        )
        self.registrar.multilingual_handler_registration(
            aiogram_register_func=dp.register_message_handler,
            handler=self.contact,
            pattern_or_list='kb_reply_contact',
            handler_type='text'
        )
        self.registrar.multilingual_handler_registration(
            aiogram_register_func=dp.register_message_handler,
            handler=self.about,
            pattern_or_list='kb_reply_about',
            handler_type='text'
        )
        self.registrar.multilingual_handler_registration(
            aiogram_register_func=dp.register_message_handler,
            handler=self.to_main,
            pattern_or_list='kb_reply_main_menu',
            handler_type='text'
        )

    async def help_main(self, message: types.Message):
        await self.message_manager.send_message('help_main')

    async def contact(self, message: types.Message):
        await self.message_manager.send_message('contact_text')

    async def about(self, message: types.Message):
        await self.message_manager.send_message('about')

    async def to_main(self, message: types.Message):
        await self.message_manager.send_message('to_main_menu')
