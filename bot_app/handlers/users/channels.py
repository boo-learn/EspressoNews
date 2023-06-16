import asyncio

from aiogram import types
from aiogram.dispatcher import FSMContext

from bot_app.data.messages import gen_sure_unsubscribe_mess
from bot_app.keyboards.inlines import ikb_unsubscribe, ikb_my_channels
from bot_app.loader import dp
from bot_app.states import DeleteChannelStates
from bot_app.utils import delete_previus_message_for_feedback
from bot_app.utils.find_button_index import find_button_index


@dp.callback_query_handler(text_contains='choose_channel_', state=DeleteChannelStates.choose_channel_for_delete)
async def choose_channel_callback(call: types.CallbackQuery, state: FSMContext):
    choose_channel = call.data.split('_')[-1]

    await state.update_data(choose_channel_for_delete=choose_channel)
    await call.message.answer(gen_sure_unsubscribe_mess(choose_channel), reply_markup=ikb_unsubscribe)


@dp.callback_query_handler(text='unsubscribe', state=DeleteChannelStates.choose_channel_for_delete)
async def unsubscribe_from_channel(call: types.CallbackQuery, state: FSMContext):
    state_data = await state.get_data('choose_channel_for_delete')

    await delete_previus_message_for_feedback(call)
    await call.message.delete()

    # Удаление канала из бд
    print(f'{state_data["choose_channel_for_delete"]} удалён')

    # Удаление кнопки с каналом из frontend части
    button_index = find_button_index(state_data["choose_channel_for_delete"], ikb_my_channels)

    if button_index:
        ikb_my_channels.inline_keyboard[button_index[0]].pop(button_index[1])

    await state.finish()

    if ikb_my_channels.inline_keyboard[0]:
        await call.message.answer(text='Список каналов:', reply_markup=ikb_my_channels)
        await DeleteChannelStates.choose_channel_for_delete.set()
    else:
        await call.message.answer(text='Пока что вы не подписаны не на какие каналы.')


@dp.callback_query_handler(text='do not unsubscribe', state=DeleteChannelStates.choose_channel_for_delete)
async def unsubscribe_from_channel(call: types.CallbackQuery, state: FSMContext):
    await delete_previus_message_for_feedback(call)
    await call.message.delete()

    await state.finish()
    await call.message.answer(text='Список каналов:', reply_markup=ikb_my_channels)
    await DeleteChannelStates.choose_channel_for_delete.set()



