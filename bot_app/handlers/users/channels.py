import logging

from aiogram import types
from aiogram.dispatcher import FSMContext

from bot_app.data.messages import gen_sure_unsubscribe_mess
from bot_app.databases.cruds import SubscriptionCRUD, ChannelCRUD
from bot_app.keyboards.inlines import get_sure_unsubscribe_ikb
from bot_app.loader import dp
from bot_app.logic import ChannelLogicHandler
from bot_app.states import ChannelStates
from bot_app.utils import delete_previus_message_for_feedback

logger = logging.getLogger(__name__)


@dp.callback_query_handler(text_contains='choose_channel_')
async def choose_channel_callback(call: types.CallbackQuery, state: FSMContext):
    logger.debug('Entering choose_channel_callback')
    choose_channel = call.data.split('_')[-1]
    await ChannelStates.choose_channel_for_delete.set()
    await state.update_data(choose_channel_for_delete=choose_channel)
    await call.message.answer(gen_sure_unsubscribe_mess(choose_channel), reply_markup=get_sure_unsubscribe_ikb())
    logger.info('Exiting choose_channel_callback')


@dp.callback_query_handler(text='unsubscribe', state=ChannelStates.choose_channel_for_delete)
async def unsubscribe_from_channel(call: types.CallbackQuery, state: FSMContext):
    logger.debug('Entering unsubscribe_from_channel')
    state_data = await state.get_data('choose_channel_for_delete')
    channel_username = state_data['choose_channel_for_delete']

    await delete_previus_message_for_feedback(call)
    await call.message.delete()

    subscription_crud = SubscriptionCRUD()
    channel_crud = ChannelCRUD()

    channel = await channel_crud.get_channel(channel_username)

    logger.info(f'Channel object for delete {channel}')

    subscription_for_delete = await subscription_crud.get_subscription(call.from_user.id, channel)

    logger.info(f'Subscription for delete object {subscription_for_delete}')

    await subscription_crud.delete_subscription(subscription_for_delete)

    await subscription_crud.check_channel_and_delete_if_empty(channel)

    logic_handler = ChannelLogicHandler()
    await logic_handler.send_channels_list_to_user_after_remove(channel.channel_name, call.message, state)
    logger.info('Exiting unsubscribe_from_channel')


@dp.callback_query_handler(text='do not unsubscribe', state=ChannelStates.choose_channel_for_delete)
async def unsubscribe_from_channel(call: types.CallbackQuery, state: FSMContext):
    logger.debug('Entering do_not_unsubscribe_from_channel')
    await delete_previus_message_for_feedback(call)
    await call.message.delete()

    await state.finish()

    logic_handler = ChannelLogicHandler()
    await logic_handler.send_channels_list_to_user(call, True)
    logger.info('Exiting do_not_unsubscribe_from_channel')
