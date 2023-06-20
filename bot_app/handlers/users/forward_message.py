from aiogram import types
from aiogram.dispatcher import FSMContext

from bot_app.data.messages import gen_success_subscribe_mess, gen_subscribe_failed_mess
from bot_app.databases.cruds import ChannelCRUD, SubscriptionCRUD
from bot_app.keyboards.inlines import get_sure_subscribe_ikb
from bot_app.loader import dp
from bot_app.states.channels import ChannelStates
from bot_app.utils import delete_previus_message_for_feedback


# в функцию не передаётся members count
@dp.message_handler(content_types=types.ContentTypes.ANY)
async def action_forward_message(message: types.Message, state: FSMContext):
    if message.forward_from_chat:
        channel_username = message.forward_from_chat.username
        members_count = await message.forward_from_chat.get_members_count()

        if not channel_username:
            await message.reply(
                gen_subscribe_failed_mess(),
            )

            return False

        await ChannelStates.forward_message_channel.set()
        await state.update_data(forward_message_channel=channel_username)

        channel_crud = ChannelCRUD()
        subscription_crud = SubscriptionCRUD()

        channel = await channel_crud.check_channel_and_create_if_empty(
            channel_username,
            message.forward_from_chat.full_name,
            message.forward_from_chat.invite_link,
            message.forward_from_chat.description,
            members_count
        )

        await subscription_crud.update_subscription(message.from_user.id, channel, True)

        await message.reply(
            gen_success_subscribe_mess(message.forward_from_chat.full_name),
            reply_markup=get_sure_subscribe_ikb(channel_username)
        )

        await state.finish()


@dp.callback_query_handler(text_contains='do not subscribe')
async def subscribe_to_the_channel(call: types.CallbackQuery):
    channel_username = call.data.split('&shash&')[-1]

    await delete_previus_message_for_feedback(call)
    await call.message.delete()

    channel_crud = ChannelCRUD()
    subscription_crud = SubscriptionCRUD()

    # отпишись и удались
    channel = await channel_crud.get_channel(channel_username)
    await subscription_crud.update_subscription(call.message.from_user.id, channel)
    await channel_crud.check_channel_and_delete_if_empty(channel)

