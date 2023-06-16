from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

ikb_help = InlineKeyboardMarkup(
    row_width=1,
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Вопрос 1', callback_data='question_1'),
            InlineKeyboardButton(text='Вопрос 2', callback_data='question_2'),
            InlineKeyboardButton(text='Вопрос 3', callback_data='question_3'),
            InlineKeyboardButton(text='Вопрос 4', callback_data='question_4'),
            InlineKeyboardButton(text='Вопрос 5', callback_data='question_5'),
        ]

    ]
)
