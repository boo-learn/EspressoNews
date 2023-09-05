from aiogram.dispatcher.filters.state import StatesGroup, State


class ChannelStates(StatesGroup):
    choose_channel_for_delete = State()
    forward_message_channel = State()
