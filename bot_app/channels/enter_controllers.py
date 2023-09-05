import logging
from typing import List

from bot_app.channels.cruds import SubscriptionCRUD
from shared.models import Channel

logger = logging.getLogger(__name__)


class ChannelLogicHandler:
    @staticmethod
    async def send_channels_list_to_user(
            aiogram_message_manager,
            user_id,
    ):
        subscription_crud = SubscriptionCRUD()
        subscribed_channels: List[Channel] = await subscription_crud.get_subscribed_channels(user_id)

        if subscribed_channels:
            await aiogram_message_manager.send_message('channel_list', dynamic_keyboard_parameters=subscribed_channels)
        else:
            await aiogram_message_manager.send_message('not_subscribed_channels')

    async def send_channels_list_to_user_after_remove(
            self,
            aiogram_message_manager,
            channel_name,
            user_id,
            state,
    ):
        subscription_crud = SubscriptionCRUD()
        subscribed_channels: List[Channel] = await subscription_crud.get_subscribed_channels(user_id)
        logger.info(f"User {user_id} is currently subscribed to {len(subscribed_channels)} channels.")

        self.lazy_remove_channel(subscribed_channels, channel_name)

        await state.finish()

        if subscribed_channels:
            await aiogram_message_manager.send_message('channel_list', dynamic_keyboard_parameters=subscribed_channels)
            logger.info(f"Sent updated channel list to user {user_id}.")
        else:
            await aiogram_message_manager.send_message('not_subscribed_channels')
            logger.info(f"Informed user {user_id} that they have no channel subscriptions.")

    @staticmethod
    def lazy_remove_channel(subscribed_channels, channel_name):
        to_remove_index = None

        for index, channel in enumerate(subscribed_channels):
            if channel[0].channel_name == channel_name:
                to_remove_index = index
                break

        if to_remove_index is not None:
            del subscribed_channels[to_remove_index]
