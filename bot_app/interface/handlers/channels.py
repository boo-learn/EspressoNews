import logging

from aiogram import types
from aiogram.dispatcher import FSMContext

from bot_app.channels.cruds import SubscriptionCRUD, ChannelCRUD
from bot_app.loader import dp
from bot_app.channels.enter_controllers import ChannelLogicHandler
from bot_app.core.tools.handler_tools import HandlersTools
from bot_app.interface.states import ChannelStates

logger = logging.getLogger(__name__)


class ChannelsHandlers(HandlersTools):
    def __init__(self):
        super().__init__()
        self.register_handlers()
        self.channel_crud = ChannelCRUD()
        self.logic_handler = ChannelLogicHandler()
        self.subscription_crud = SubscriptionCRUD()

    def register_handlers(self):
        self.registrar.simply_handler_registration(
            dp.register_callback_query_handler,
            self.choose_channel_callback,
            'choose_channel_',
            'text_contains'
        )
        self.registrar.simply_handler_registration(
            dp.register_callback_query_handler,
            self.unsubscribe_from_channel,
            'unsubscribe',
            'text',
            ChannelStates.choose_channel_for_delete
        )
        self.registrar.simply_handler_registration(
            dp.register_callback_query_handler,
            self.unsubscribe_from_channel,
            'do not unsubscribe',
            'text',
            ChannelStates.choose_channel_for_delete
        )

    async def choose_channel_callback(self, call: types.CallbackQuery, state: FSMContext):
        choose_channel: str = call.data.split('_')[-1]
        await ChannelStates.choose_channel_for_delete.set()
        await state.update_data(choose_channel_for_delete=choose_channel)
        await self.message_manager.send_message('sure_unsubscribe', channel_title=choose_channel)
        logger.info('Exiting choose_channel_callback')

    async def unsubscribe_from_channel(self, call: types.CallbackQuery, state: FSMContext):
        logger.debug('Entering unsubscribe_from_channel')
        state_data = await state.get_data('choose_channel_for_delete')
        channel_id = state_data['choose_channel_for_delete']

        await self.message_manager.delete_previous_message()
        await call.message.delete()

        logger.info(f'Channel username for delete {channel_id}')
        channel = await self.channel_crud.get_channel_by_id(channel_id)

        subscription_for_delete = await self.subscription_crud.get_subscription(call.from_user.id, channel)
        logger.info(f'Subscription for delete object {subscription_for_delete}')

        await self.subscription_crud.delete_subscription(subscription_for_delete)

        await self.subscription_crud.check_channel_and_delete_if_empty(channel)

        await self.logic_handler.send_channels_list_to_user_after_remove(
            self.message_manager,
            channel.channel_name,
            call.from_user.id,
            state,
        )
        logger.info('Exiting unsubscribe_from_channel')

    async def not_unsubscribe(self, call: types.CallbackQuery, state: FSMContext):
        logger.debug('Entering do_not_unsubscribe_from_channel')
        user_id = call.from_user.id

        await self.message_manager.delete_previous_message()
        await call.message.delete()

        await state.finish()

        logic_handler = ChannelLogicHandler()
        await logic_handler.send_channels_list_to_user(self.message_manager, user_id)
        logger.info('Exiting do_not_unsubscribe_from_channel')
