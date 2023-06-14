from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

ikb_start = InlineKeyboardMarkup(
    row_width=1,
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Погнали!', callback_data='Погнали!')
        ]

    ]
)

ikb_after_start = InlineKeyboardMarkup(
    row_width=2,
    inline_keyboard=[
        [
            InlineKeyboardButton(text='1', callback_data='adding first method'),
            InlineKeyboardButton(text='2', callback_data='adding second method'),
        ]

    ]
)
