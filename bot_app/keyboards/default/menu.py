from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

kb_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Мои каналы'),
            KeyboardButton(text='Настройки'),
        ],
        [
            KeyboardButton(text='Подписка'),
            KeyboardButton(text='Помощь'),
        ],
    ],
    resize_keyboard=True
)
