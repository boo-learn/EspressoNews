from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

ikb_back = InlineKeyboardMarkup(row_width=1)

back_button = InlineKeyboardButton(text='вернуться', callback_data='return')

ikb_back.add(back_button)
