from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton

from bot_app.data.messages import gen_sure_subscribe_mess, gen_success_subscribe_mess
from bot_app.keyboards.inlines.channels import ikb_subscribe
from bot_app.loader import dp
from bot_app.states.channels import ChannelStates
from bot_app.utils import delete_previus_message_for_feedback, delete_previus_previus_message_for_feedback


@dp.message_handler(content_types=types.ContentTypes.ANY)
async def action_forward_message(message: types.Message, state: FSMContext):
    if message.forward_from_chat:
        channel_data = message.forward_from_chat
        channel = channel_data.username or channel_data.title

        await ChannelStates.forward_message_channel.set()
        await state.update_data(forward_message_channel=channel)

        button = InlineKeyboardButton(text='Да', callback_data=f'subscribe&slash&{channel}')
        ikb_subscribe.insert(button)

        await message.reply(
            gen_sure_subscribe_mess(channel_data),
            reply_markup=ikb_subscribe
        )

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

