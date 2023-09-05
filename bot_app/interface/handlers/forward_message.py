import logging

from aiogram import types
from aiogram.dispatcher import FSMContext

from bot_app.channels.cruds import ChannelCRUD, SubscriptionCRUD
from bot_app.loader import dp
from bot_app.core.tools.handler_tools import HandlersTools
from bot_app.core.messages.senders import ReplySender
from bot_app.interface.states import ChannelStates

logger = logging.getLogger(__name__)


class ForwardHandlers(HandlersTools):
    def __init__(self):
        super().__init__()
        self.register_routes()
        self.channel_crud = ChannelCRUD()
        self.subscription_crud = SubscriptionCRUD()

    def register_routes(self):
        self.aiogram_registrar.simply_handler_registration(
            dp.register_message_handler,
            self.action_forward_message,
            types.ContentTypes.ANY,
            'content_types',

        )
        self.aiogram_registrar.simply_handler_registration(
            dp.register_callback_query_handler,
            self.unsubscribe_to_the_channel,
            'do not subscribe',
            'text_contains'
        )

    # в функцию не передаётся members count
    async def action_forward_message(self, message: types.Message, state: FSMContext):
        logger.debug('Starting action_forward_message function')
        if message.forward_from_chat is not None and message.forward_from_chat['type'] == 'channel':
            channel_username = message.forward_from_chat.username
            members_count = await message.forward_from_chat.get_members_count()

            self.aiogram_message_manager.set_sender(ReplySender())

            if not channel_username:
                logger.warning('Channel username not found')
                await self.aiogram_message_manager.send_message('subscribe_failed')
                return False

            await ChannelStates.forward_message_channel.set()
            await state.update_data(forward_message_channel=channel_username)

            channel_id = message.forward_from_chat.id
            if channel_id < 0:
                channel_id += 1000000000000
            channel_id = abs(channel_id)

            channel = await self.channel_crud.check_channel_and_create_if_empty(
                channel_id,
                channel_username,
                message.forward_from_chat.full_name,
                message.forward_from_chat.invite_link,
                message.forward_from_chat.description,
                members_count
            )

            await self.subscription_crud.update_subscription(message.from_user.id, channel, True)

            await self.aiogram_message_manager.send_message(
                'success_subscribe',
                dynamic_keyboard_parameters=channel_username,
                channel_title=message.forward_from_chat.full_name
            )

            await state.finish()
            logger.debug('Finished action_forward_message function')

    async def unsubscribe_to_the_channel(self, call: types.CallbackQuery):
        channel_username = call.data.split('&slash&')[-1]

        logger.debug(f'Channel username: {channel_username}')

        await call.message.delete()
        logger.debug('Deleted call message')

        channel = await self.channel_crud.get_channel(channel_username)
        logger.debug(f'Fetched channel: {channel}')

        await self.subscription_crud.update_subscription(call.from_user.id, channel, False)
        logger.debug('Updated subscription')

        channel = await self.channel_crud.get_channel(channel_username)
        logger.debug(f'Fetched channel: {channel}')

        await self.channel_crud.check_channel_and_delete_if_empty(channel)
        logger.debug('Checked channel and deleted if empty')
        logger.debug('Finished unsubscribe_to_the_channel function')
