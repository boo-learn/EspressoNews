from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_donate_button():
    ikb_donate = InlineKeyboardMarkup(row_width=1)
    donate_button = InlineKeyboardButton(text='Отблагодарить', url="https://t.me/espressonewsabout/7")
    ikb_donate.add(donate_button)
    return ikb_donate
