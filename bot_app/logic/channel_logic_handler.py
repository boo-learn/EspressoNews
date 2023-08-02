import logging

from bot_app.databases.cruds import SubscriptionCRUD
from bot_app.keyboards.inlines.channels import get_choose_channels_ikb

logger = logging.getLogger(__name__)


class ChannelLogicHandler:
    @staticmethod
    async def send_channels_list_to_user(call_or_message, if_callback_func=False):
        user_id = call_or_message.from_user.id

        if if_callback_func:
            call_or_message = call_or_message.message

        subscription_crud = SubscriptionCRUD()
        subscribed_channels = await subscription_crud.get_subscribed_channels(user_id)

        if subscribed_channels:
            ikb_my_channels = get_choose_channels_ikb(subscribed_channels)
            await call_or_message.answer(text="Список каналов:", reply_markup=ikb_my_channels)
        else:
            await call_or_message.answer(text="Пока что вы не подписаны не на какие каналы.")

    async def send_channels_list_to_user_after_remove(self, channel_name, user_id, state):
        logger.info(f"Processing removal of channel {channel_name} for user {user_id}.")

        subscription_crud = SubscriptionCRUD()
        subscribed_channels = await subscription_crud.get_subscribed_channels(user_id)
        logger.info(f"User {user_id} is currently subscribed to {len(subscribed_channels)} channels.")

        ikb_my_channels = get_choose_channels_ikb(subscribed_channels)

        button_index = self.find_button_index(channel_name, ikb_my_channels)

        if button_index:
            ikb_my_channels.inline_keyboard[button_index[0]].pop(button_index[1])
            logger.info(f"Removed channel {channel_name} from the user {user_id}'s channel list.")

        await state.finish()

        if subscribed_channels:
            await message.answer(text='Список каналов:', reply_markup=ikb_my_channels)
            logger.info(f"Sent updated channel list to user {user_id}.")
        else:
            await message.answer(text='Пока что вы не подписаны не на какие каналы.')
            logger.info(f"Informed user {user_id} that they have no channel subscriptions.")

    @staticmethod
    def find_button_index(button_text, button_object):
        for i, row in enumerate(button_object.inline_keyboard):
            for j, button in enumerate(row):
                if button.text == button_text:
                    return i, j
        return None
