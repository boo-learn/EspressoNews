from aiogram.dispatcher.filters.state import StatesGroup, State


class StartStates(StatesGroup):
    overall = State()
    reading_name = State()
