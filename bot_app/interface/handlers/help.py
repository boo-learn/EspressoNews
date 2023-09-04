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
            dp.register_message_handler,
            self.cmd_help,
            'cmd_help',
            'command'
        )
        self.registrar.simply_handler_registration(
            dp.register_callback_query_handler,
            self.answers_to_the_questions,
            'question_',
            'text_contains'
        )

    async def cmd_help(self, message: types.Message):
        await self.message_manager.send_message('help', first_name=message.from_user.first_name)
        await self.message_manager.send_message('frequent_questions')

    async def answers_to_the_questions(self, call: CallbackQuery):
        message_key = 'answer_to_question_' + call.data.split('_')[-1]
        await self.message_manager.send_message(message_key)
