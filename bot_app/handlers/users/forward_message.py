import logging
from aiogram import types
from aiogram.dispatcher import FSMContext

from bot_app.data.messages import gen_success_subscribe_mess, gen_subscribe_failed_mess
from bot_app.databases.cruds import ChannelCRUD, SubscriptionCRUD
from bot_app.keyboards.inlines import get_sure_subscribe_ikb
from bot_app.loader import dp
from bot_app.states.channels import ChannelStates
from bot_app.utils import delete_previus_message_for_feedback

logger = logging.getLogger(__name__)


# в функцию не передаётся members count
@dp.message_handler(content_types=types.ContentTypes.ANY)
async def action_forward_message(message: types.Message, state: FSMContext):
    logger.debug('Starting action_forward_message function')
    if message.forward_from_chat['type'] == 'channel':
        channel_username = message.forward_from_chat.username
        members_count = await message.forward_from_chat.get_members_count()

        if not channel_username:
            logger.warning('Channel username not found')
            await message.reply(
                gen_subscribe_failed_mess(),
            )

            return False

        await ChannelStates.forward_message_channel.set()
        await state.update_data(forward_message_channel=channel_username)

        channel_crud = ChannelCRUD()
        subscription_crud = SubscriptionCRUD()

        channel_id = message.forward_from_chat.id
        if channel_id < 0:
            channel_id += 1000000000000
        channel_id = abs(channel_id)

        channel = await channel_crud.check_channel_and_create_if_empty(
            channel_id,
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
        logger.debug('Finished action_forward_message function')


@dp.callback_query_handler(text_contains='do not subscribe')
async def unsubscribe_to_the_channel(call: types.CallbackQuery):
    logger.debug('Starting unsubscribe_to_the_channel function')
    channel_username = call.data.split('&slash&')[-1]

    logger.debug(f'Channel username: {channel_username}')

    await delete_previus_message_for_feedback(call)
    logger.debug('Deleted previous message for feedback')

    await call.message.delete()
    logger.debug('Deleted call message')

    channel_crud = ChannelCRUD()
    subscription_crud = SubscriptionCRUD()

    logger.debug('Created channel_crud and subscription_crud objects')

    channel = await channel_crud.get_channel(channel_username)
    logger.debug(f'Fetched channel: {channel}')

    await subscription_crud.update_subscription(call.from_user.id, channel, False)
    logger.debug('Updated subscription')

    channel = await channel_crud.get_channel(channel_username)
    logger.debug(f'Fetched channel: {channel}')

    await channel_crud.check_channel_and_delete_if_empty(channel)
    logger.debug('Checked channel and deleted if empty')

    logger.debug('Finished unsubscribe_to_the_channel function')
