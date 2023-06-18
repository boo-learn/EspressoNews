from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton

from bot_app.crud.crud import update_subscription, get_channel, create_channel
from bot_app.data.messages import gen_sure_subscribe_mess, gen_success_subscribe_mess
from bot_app.keyboards.inlines.channels import ikb_subscribe
from bot_app.loader import dp
from bot_app.states.channels import ChannelStates
from bot_app.utils import delete_previus_message_for_feedback, delete_previus_previus_message_for_feedback
from shared.config import RABBIT_HOST
from shared.database import SessionLocal
from shared.rabbitmq import Producer, QueuesType


@dp.message_handler(content_types=types.ContentTypes.ANY)
async def action_forward_message(message: types.Message, state: FSMContext):
    if message.forward_from_chat:
        channel_data = message.forward_from_chat
        channel_username = channel_data.username
        channel_name = channel_data.title

        await ChannelStates.forward_message_channel.set()
        await state.update_data(forward_message_channel=channel_username)

        button = InlineKeyboardButton(text='Да', callback_data=f'subscribe&slash&{channel_username}')
        ikb_subscribe.insert(button)

        await message.reply(
            gen_sure_subscribe_mess(channel_data),
            reply_markup=ikb_subscribe
        )
        session = SessionLocal()

        channel = get_channel(session, channel_username)
        if not channel:
            channel = create_channel(session, channel_username, channel_name, channel_data)
            # Вызовите вашу дополнительную функцию здесь
            producer = Producer(host=RABBIT_HOST)
            await producer.send_message(message='subscribe', queue=QueuesType.subscription_service)
            await producer.close()

        user_id = message.from_user.id
        update_subscription(session, user_id, channel)

        await state.finish()


@dp.callback_query_handler(text_contains='subscribe&slash&')
async def unsubscribe_from_channel(call: types.CallbackQuery):
    channel = call.data.split('&slash&')[-1]

    await delete_previus_message_for_feedback(call)
    await call.message.delete()

    # Занесение в бд подписки
    # В forward_channel приходит username или title, потому что у некоторых каналов нет username, так как он скрыт.
    # Нужно уточнить момент у Бори, если что ебану проверку на пустоту username

    await call.message.answer(
        gen_success_subscribe_mess()
    )


@dp.callback_query_handler(text_contains='do not subscribe')
async def unsubscribe_from_channel(call: types.CallbackQuery):
    await delete_previus_message_for_feedback(call)
    await call.message.delete()

