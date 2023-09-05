import logging

from aiogram import types
from aiogram.types import CallbackQuery

from bot_app.core.users.crud import UserCRUD
from bot_app.loader import dp
from bot_app.core.tools.handler_tools import HandlersTools
from bot_app.interface.states import StartStates
from aiogram.dispatcher import FSMContext

logger = logging.getLogger(__name__)


class StartHandlers(HandlersTools):
    def __init__(self):
        super().__init__()
        self.register_handlers()
        self.user_crud = UserCRUD()

    def register_handlers(self):
        self.registrar.simply_handler_registration(
            aiogram_register_func=dp.register_message_handler,
            handler=self.start_command,
            pattern_or_list='start',
            handler_type='command'
        )
        # self.registrar.simply_handler_registration(
        #     aiogram_register_func=dp.register_callback_query_handler,
        #     handler=self.action_after_start_btn,
        #     pattern_or_list="Погнали!",
        #     handler_type='text'
        # )
        # self.registrar.simply_handler_registration(
        #     aiogram_register_func=dp.register_callback_query_handler,
        #     handler=self.return_action,
        #     pattern_or_list='return',
        #     handler_type='text'
        # )
        self.registrar.multilingual_handler_registration(
            aiogram_register_func=dp.register_message_handler,
            handler=self.ask_for_name,
            pattern_or_list='Настроить сейчас ✅',
            handler_type='text'
        )
        self.registrar.multilingual_handler_registration(
            aiogram_register_func=dp.register_message_handler,
            handler=self.default_settings,
            pattern_or_list='Настроить позже ➡',
            handler_type='text'
        )
        self.registrar.simply_handler_registration(
            aiogram_register_func=dp.register_message_handler,
            handler=self.read_new_name,
            pattern_or_list=None,
            handler_type='always',
            state=StartStates.reading_name
        )
        self.registrar.simply_handler_registration(
            aiogram_register_func=dp.register_callback_query_handler,
            handler=self.keep_name,
            pattern_or_list='keep_name_cb',
            handler_type='text',
            state=StartStates.reading_name
        )
        self.registrar.simply_handler_registration(
            aiogram_register_func=dp.register_callback_query_handler,
            handler=self.read_intonation,
            pattern_or_list='cb_intonation_',
            handler_type='text_contains',
        )


    async def start_command(self, message: types.Message):
        await self.message_manager.send_message(
            key='start',
            first_name=message.from_user.first_name
        )

    async def ask_for_name(self, message: types.Message):
        await self.message_manager.send_message(
            key='ask_for_name',
            first_name=message.from_user.first_name,
        )
        await StartStates.reading_name.set()

    async def read_new_name(self, message: types.Message, state: FSMContext):
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
        await self.message_manager.send_message(
            key='ask_for_intonation'
        )

    async def keep_name(self, call: CallbackQuery, state: FSMContext):
        await call.message.delete_reply_markup()
        await call.answer()
        await self.message_manager.send_message(
            key='accepted_new_name',
            first_name=call.from_user.first_name,
        )
        await state.reset_state(with_data=False)
        await self.message_manager.send_message(
            key='ask_for_intonation'
        )

    async def read_intonation(self, call: CallbackQuery):
        await call.answer()
        await call.message.delete_reply_markup()
        intonation = call.data[14:]
        await self.user_crud.update_user_intonation(

            call.from_user.id,

            intonation
        )
        if intonation == 'Official':
            await self.message_manager.send_message(
                key='intonation_set_official',
                intonation=intonation
            )
        else:
            await self.message_manager.send_message(
                key='intonation_set_sarcastic',
                intonation=intonation
            )
        await self.message_manager.send_message(
            key='settings_complete',
            intonation=intonation
        )

    async def default_settings(self, message: types.Message):
        await self.message_manager.send_message(
            key='default_settings',
            first_name=message.from_user.first_name
        )
    # async def action_after_start_btn(self, call: CallbackQuery):
    #     message_obj = call.message
    #
    #     await self.message_manager.delete_before_message()
    #     await message_obj.delete()
    #     await self.message_manager.send_message('manual')
    #
    #     await self.message_manager.send_message(
    #         'after_start_btn',
    #         first_name=call.from_user.first_name
    #     )
    #     logger.debug('Message after start button sent')
    #
    # async def return_action(self, call: CallbackQuery):
    #     message_obj = call.message
    #     await self.message_manager.delete_before_message()
    #     await message_obj.delete()
    #     await self.message_manager.send_message('return')
