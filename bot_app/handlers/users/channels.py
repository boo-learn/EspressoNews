from aiogram import types
from aiogram.dispatcher import FSMContext

from bot_app.data.messages import gen_sure_unsubscribe_mess
from bot_app.keyboards.inlines import ikb_unsubscribe, ikb_my_channels
from bot_app.loader import dp
from bot_app.states import ChannelStates
from bot_app.utils import delete_previus_message_for_feedback
from bot_app.utils.find_button_index import find_button_index
from shared.config import RABBIT_HOST
from shared.models import Channel, Subscription
from shared.database import SessionLocal
from shared.rabbitmq import Producer, QueuesType


@dp.callback_query_handler(text_contains='choose_channel_')
async def choose_channel_callback(call: types.CallbackQuery, state: FSMContext):
    choose_channel = call.data.split('_')[-1]
    await ChannelStates.choose_channel_for_delete.set()
    await state.update_data(choose_channel_for_delete=choose_channel)
    await call.message.answer(gen_sure_unsubscribe_mess(choose_channel), reply_markup=ikb_unsubscribe)


@dp.callback_query_handler(text='unsubscribe', state=ChannelStates.choose_channel_for_delete)
async def unsubscribe_from_channel(call: types.CallbackQuery, state: FSMContext):
    state_data = await state.get_data('choose_channel_for_delete')

    await delete_previus_message_for_feedback(call)
    await call.message.delete()

    channel_name = state_data["choose_channel_for_delete"]
    session = SessionLocal()

    # Get the channel and subscription objects
    channel = session.query(Channel).filter(Channel.channel_name == channel_name).first()
    subscription = session.query(Subscription).filter(Subscription.channel_id == channel.channel_id,
                                                      Subscription.user_id == call.from_user.id).first()

    # Delete the subscription from the database
    session.delete(subscription)
    session.commit()
    print(f'Subscription for {channel_name} deleted')

    # Check if there are no remaining subscriptions for the channel
    remaining_subscriptions = session.query(Subscription).filter(Subscription.channel_id == channel.channel_id).count()

    if remaining_subscriptions == 0:
        # Delete the channel from the database
        session.delete(channel)
        session.commit()
        print(f'{channel_name} deleted')

        # Шлем сообщение в редис
        producer = Producer(host=RABBIT_HOST)
        await producer.send_message(message='unsubscribe', queue=QueuesType.subscription_service)
        await producer.close()

    # Delete the button with the channel from the frontend part
    button_index = find_button_index(channel_name, ikb_my_channels)

    if button_index:
        ikb_my_channels.inline_keyboard[button_index[0]].pop(button_index[1])

    await state.finish()

    if ikb_my_channels.inline_keyboard[0]:
        await call.message.answer(text='Список каналов:', reply_markup=ikb_my_channels)
    else:
        await call.message.answer(text='Пока что вы не подписаны не на какие каналы.')


@dp.callback_query_handler(text='do not unsubscribe', state=ChannelStates.choose_channel_for_delete)
async def unsubscribe_from_channel(call: types.CallbackQuery, state: FSMContext):
    await delete_previus_message_for_feedback(call)
    await call.message.delete()

    await state.finish()
    await call.message.answer(text='Список каналов:', reply_markup=ikb_my_channels)
