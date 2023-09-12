from aiogram.dispatcher.filters.state import StatesGroup, State


class SocialNetworkStates(StatesGroup):
    enter_email = State()
