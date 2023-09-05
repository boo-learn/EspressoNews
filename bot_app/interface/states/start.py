from aiogram.dispatcher.filters.state import StatesGroup, State


class StartStates(StatesGroup):
    reading_name = State()
