from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

kb_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Мои каналы'),
            KeyboardButton(text='Настройки'),
        ],
        [
            KeyboardButton(text='Донат'),
        ],
    ],
    resize_keyboard=True
)
