from bot_app.databases.cruds import SubscriptionCRUD
from bot_app.keyboards.inlines.channels import get_choose_channels_ikb


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

    async def send_channels_list_to_user_after_remove(self, channel_name, message, state):
        user_id = message.from_user.id

        subscription_crud = SubscriptionCRUD()
        subscribed_channels = await subscription_crud.get_subscribed_channels(user_id)

        ikb_my_channels = get_choose_channels_ikb(subscribed_channels)

        button_index = self.find_button_index(channel_name, ikb_my_channels)

        if button_index:
            ikb_my_channels.inline_keyboard[button_index[0]].pop(button_index[1])

        await state.finish()

        if subscribed_channels:
            await message.answer(text='Список каналов:', reply_markup=ikb_my_channels)
        else:
            await message.answer(text='Пока что вы не подписаны не на какие каналы.')

    @staticmethod
    def find_button_index(button_text, button_object):
        for i, row in enumerate(button_object.inline_keyboard):
            for j, button in enumerate(row):
                if button.text == button_text:
                    return i, j
        return None
