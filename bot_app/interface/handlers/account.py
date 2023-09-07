import logging

from aiogram import types
from aiogram.types import CallbackQuery

from bot_app.core.users.crud import UserCRUD
from bot_app.loader import dp
from bot_app.core.tools.handler_tools import HandlersTools
from bot_app.interface.states import AccountStates
from aiogram.dispatcher import FSMContext

logger = logging.getLogger(__name__)


class AccountHandlers(HandlersTools):
    def __init__(self):
        super().__init__()
        self.register_handlers()
        self.user_crud = UserCRUD()

    def register_handlers(self):
        self.registrar.multilingual_handler_registration(
            aiogram_register_func=dp.register_message_handler,
            handler=self.account_main,
            pattern_or_list='kb_reply_lk',
            handler_type='text'
        )
        self.registrar.multilingual_handler_registration(
            aiogram_register_func=dp.register_message_handler,
            handler=self.ask_for_intonation,
            pattern_or_list='kb_reply_change_intonation',
            handler_type='text'
        )
        self.registrar.multilingual_handler_registration(
            aiogram_register_func=dp.register_message_handler,
            handler=self.ask_for_name,
            pattern_or_list='kb_reply_change_name',
            handler_type='text'
        )
        self.registrar.multilingual_handler_registration(
            aiogram_register_func=dp.register_message_handler,
            handler=self.ask_for_language,
            pattern_or_list='kb_reply_change_language',
            handler_type='text'
        )
        self.registrar.simply_handler_registration(
            aiogram_register_func=dp.register_callback_query_handler,
            handler=self.read_intonation,
            pattern_or_list='cb_intonation_',
            handler_type='text_contains',
        )
        self.registrar.simply_handler_registration(
            aiogram_register_func=dp.register_message_handler,
            handler=self.read_name,
            pattern_or_list=None,
            handler_type='always',
            state=AccountStates.reading_name
        )
        self.registrar.simply_handler_registration(
            aiogram_register_func=dp.register_callback_query_handler,
            handler=self.read_language,
            pattern_or_list='cb_language_set_',
            handler_type='text_contains',
        )

    async def account_main(self, message: types.Message):
        await self.message_manager.send_message(
            key='account_main'
        )

    async def ask_for_intonation(self, message: types.Message):
        await self.message_manager.send_message(
            key='ask_for_intonation'
        )

    async def read_intonation(self, call: CallbackQuery):
        await call.answer()
        intonation = call.data[14:]
        await self.user_crud.update_user_intonation(
            call.from_user.id,
            intonation
        )
        if intonation == 'Official':
            await self.message_manager.send_message(
                key='intonation_set_official'
            )
        else:
            await self.message_manager.send_message(
                key='intonation_set_sarcastic'
            )

    async def ask_for_name(self, message: types.Message):
        await AccountStates.reading_name.set()
        await self.message_manager.send_message(
            key='account_ask_for_name'
        )

    async def read_name(self, message: types.Message, state: FSMContext):
        new_name = message.text
        user = await self.user_crud.update_user_name(
            user_id=message.from_user.id,
            first_name=new_name,
        )
        await self.message_manager.send_message(
            key='accepted_new_name',
            first_name=user.first_name,
        )
        await state.reset_state(with_data=False)

    async def ask_for_language(self, message: types.Message):
        await self.message_manager.send_message(
            key='account_ask_for_language'
        )

    async def read_language(self, call: CallbackQuery):
        await call.answer()
        language_code = call.data[-2:]
        await self.user_crud.update_user_language(
            user_id=call.from_user.id,
            language_code=language_code
        )
        self.message_manager.set_language(language_code)
        await self.message_manager.send_message(
            key='language_updated'
        )
