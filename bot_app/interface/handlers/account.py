import logging

from aiogram import types
from aiogram.types import CallbackQuery

from bot_app.core.users.crud import UserCRUD
from bot_app.channels.cruds import ChannelCRUD
from bot_app.channels.cruds import SubscriptionCRUD
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
        self.subscription_crud = SubscriptionCRUD()
        self.channel_crud = ChannelCRUD()

    def register_handlers(self):
        self.aiogram_registrar.multilingual_handler_registration(
            aiogram_register_func=dp.register_message_handler,
            handler=self.account_main,
            pattern_or_list='kb_reply_lk',
            handler_type='text'
        )
        self.aiogram_registrar.multilingual_handler_registration(
            aiogram_register_func=dp.register_message_handler,
            handler=self.ask_for_intonation,
            pattern_or_list='kb_reply_change_intonation',
            handler_type='text'
        )
        self.aiogram_registrar.multilingual_handler_registration(
            aiogram_register_func=dp.register_message_handler,
            handler=self.ask_for_name,
            pattern_or_list='kb_reply_change_name',
            handler_type='text'
        )
        self.aiogram_registrar.multilingual_handler_registration(
            aiogram_register_func=dp.register_message_handler,
            handler=self.ask_for_language,
            pattern_or_list='kb_reply_change_language',
            handler_type='text'
        )
        self.aiogram_registrar.simply_handler_registration(
            aiogram_register_func=dp.register_callback_query_handler,
            handler=self.read_intonation,
            pattern_or_list='cb_intonation_',
            handler_type='text_contains',
        )
        self.aiogram_registrar.simply_handler_registration(
            aiogram_register_func=dp.register_message_handler,
            handler=self.read_name,
            pattern_or_list=None,
            handler_type='always',
            state=AccountStates.reading_name
        )
        self.aiogram_registrar.simply_handler_registration(
            aiogram_register_func=dp.register_callback_query_handler,
            handler=self.read_language,
            pattern_or_list='cb_language_set_',
            handler_type='text_contains',
        )
        self.aiogram_registrar.multilingual_handler_registration(
            aiogram_register_func=dp.register_message_handler,
            handler=self.show_channels,
            pattern_or_list='kb_reply_my_channels',
            handler_type='text'
        )
        self.aiogram_registrar.simply_handler_registration(
            aiogram_register_func=dp.register_callback_query_handler,
            handler=self.unsubscribe_from_channel,
            pattern_or_list='unsubscribe_',
            handler_type='text_contains',
        )
        self.aiogram_registrar.simply_handler_registration(
            aiogram_register_func=dp.register_callback_query_handler,
            handler=self.navigate_channels,
            pattern_or_list='^channels_.+',
            handler_type='regexp',
        )


    async def account_main(self, message: types.Message):
        await self.aiogram_message_manager.send_message(
            key='account_main'
        )

    async def ask_for_intonation(self, message: types.Message):
        await self.aiogram_message_manager.send_message(
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
            await self.aiogram_message_manager.send_message(
                key='intonation_set_official_from_account'
            )
        else:
            await self.aiogram_message_manager.send_message(
                key='intonation_set_sarcastic_from_account'
            )

    async def ask_for_name(self, message: types.Message):
        await AccountStates.reading_name.set()
        await self.aiogram_message_manager.send_message(
            key='account_ask_for_name'
        )

    async def read_name(self, message: types.Message, state: FSMContext):
        new_name = message.text
        user = await self.user_crud.update_user_name(
            user_id=message.from_user.id,
            first_name=new_name,
        )
        await self.aiogram_message_manager.send_message(
            key='accepted_new_name',
            first_name=user.first_name,
        )
        await state.reset_state(with_data=False)

    async def ask_for_language(self, message: types.Message):
        await self.aiogram_message_manager.send_message(
            key='account_ask_for_language'
        )

    async def read_language(self, call: CallbackQuery):
        await call.answer()
        language_code = call.data[-2:]
        await self.user_crud.update_user_language(
            user_id=call.from_user.id,
            language_code=language_code
        )
        self.aiogram_message_manager.set_language(language_code)
        await self.aiogram_message_manager.send_message(
            key='language_updated'
        )

    async def show_channels(self, message: types.Message, state: FSMContext):
        subscribed_channels = await self.subscription_crud.get_subscribed_channels(message.from_user.id)
        await state.update_data({
            'subscribed_channels': subscribed_channels,
            'limit': 3,
            'offset': 0
        })

        if subscribed_channels:
            await self.aiogram_message_manager.send_message(
                'channel_list',
                dynamic_keyboard_parameters=(subscribed_channels, 3, 0)
            )
        else:
            await self.aiogram_message_manager.send_message('not_subscribed_channels')

    async def navigate_channels(self, call: CallbackQuery, state: FSMContext):
        data = await state.get_data()
        subscribed_channels = data['subscribed_channels']
        limit = data['limit']
        offset = data['offset']
        if call.data == 'channels_current':
            await call.answer(str((len(subscribed_channels))))
            return
        await call.message.delete()
        if call.data == 'channels_prev':
            if offset > 0:
                offset = offset - limit
        else:
            if len(subscribed_channels) > offset + limit:
                offset = offset + limit
        await state.update_data({'offset': offset})
        await self.aiogram_message_manager.send_message(
            'channel_list',
            dynamic_keyboard_parameters=(subscribed_channels, limit, offset)
        )

    async def unsubscribe_from_channel(self, call: CallbackQuery, state: FSMContext):
        channel_id_parts = call.data.split('_')[1:]
        channel_id = '_'.join(channel_id_parts)
        channel = await self.channel_crud.get_channel_by_id(channel_id)
        subscription_for_delete = await self.subscription_crud.get_subscription(
            call.from_user.id,
            channel
        )
        await self.subscription_crud.delete_subscription(
            subscription_for_delete
        )
        await self.subscription_crud.check_channel_and_delete_if_empty(channel)
        await self.aiogram_message_manager.send_message('unsubscribed_from', channel=channel.channel_name)
        await call.message.delete()
        subscribed_channels = await self.subscription_crud.get_subscribed_channels(call.from_user.id)
        data = await state.get_data()
        await state.update_data({'subscribed_channels': subscribed_channels})
        limit = data['limit']
        offset = data['offset']
        if len(subscribed_channels) <= offset:
            offset -= limit
            await state.update_data({'offset': offset})
        if subscribed_channels:
            await self.aiogram_message_manager.send_message(
                'channel_list',
                dynamic_keyboard_parameters=(subscribed_channels, limit, offset)
            )
        else:
            await self.aiogram_message_manager.send_message('not_subscribed_channels')

