from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def generate_keyboard(buttons: list[list[str]], resize_keyboard=True) -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=resize_keyboard)
    for row in buttons:
        row_buttons = [KeyboardButton(text=button_text) for button_text in row]
        keyboard.row(*row_buttons)
    return keyboard


def get_kb_settings():
    buttons = [
        ['Периодичность', 'Интонация'],
        ['Роль', 'Главное меню']
    ]
    return generate_keyboard(buttons)


def get_kb_periodicity():
    buttons = [
        ['Каждый час', 'Каждые 3 часа'],
        ['Каждые 6 часов'],
        ['Главное меню']
    ]
    return generate_keyboard(buttons)


def get_kb_intonation():
    buttons = [
        ['Официальная'],
        ['Саркастично-шутливая'],
        ['Главное меню']
    ]
    return generate_keyboard(buttons)


def get_kb_role():
    buttons = [
        ['Диктор'],
        ['Главное меню']
    ]
    return generate_keyboard(buttons)
