from aiogram.dispatcher.filters.state import StatesGroup, State


class DeleteChannelStates(StatesGroup):
    choose_channel_for_delete = State()
