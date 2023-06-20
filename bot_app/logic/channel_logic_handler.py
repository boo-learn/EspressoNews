from bot_app.databases.cruds import SubscriptionCRUD
from bot_app.keyboards.inlines.channels import get_choose_channels_ikb


class ChannelLogicHandler:
    @staticmethod
    async def send_channels_list_to_user(message):
        user_id = message.from_user.id

        subscription_crud = SubscriptionCRUD()
        subscribed_channels = await subscription_crud.get_subscribed_channels(user_id)

        ikb_my_channels = get_choose_channels_ikb(subscribed_channels)

        if ikb_my_channels.inline_keyboard[0]:
            await message.answer(text="Список каналов:", reply_markup=ikb_my_channels)
        else:
            await message.answer(text="Пока что вы не подписаны не на какие каналы.")

    async def send_channels_list_to_user_after_remove(self, channel_name, message, state):
        user_id = message.from_user.id

        subscription_crud = SubscriptionCRUD()
        subscribed_channels = await subscription_crud.get_subscribed_channels(user_id)

        ikb_my_channels = get_choose_channels_ikb(subscribed_channels)

        button_index = self.find_button_index(channel_name, ikb_my_channels)

        if button_index:
            ikb_my_channels.inline_keyboard[button_index[0]].pop(button_index[1])

        await state.finish()

        if ikb_my_channels.inline_keyboard[0]:
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
