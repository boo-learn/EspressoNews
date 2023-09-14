from aiogram.dispatcher.filters.state import StatesGroup, State


class AccountStates(StatesGroup):
    overall = State()
    reading_name = State()
