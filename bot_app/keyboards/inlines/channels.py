from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot_app.keyboards.inlines.back import back_button

channels = ['Канал 1', 'Канал 2', 'Канал 3', 'Канал 4', 'Канал 5', 'Канал 6', 'Канал 7', 'Канал 8']

ikb_my_channels = InlineKeyboardMarkup(row_width=2)

for channel in channels:
    button = InlineKeyboardButton(text=channel, callback_data=f'choose_channel_{channel}')
    ikb_my_channels.insert(button)

# сделать пагинацию по 10 каналов


ikb_unsubscribe = InlineKeyboardMarkup(
    row_width=2,
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Да', callback_data='unsubscribe'),
            InlineKeyboardButton(text='Нет', callback_data='do not unsubscribe'),
        ]

    ]
)

# вторая кнопка добавляется динамически
ikb_subscribe = InlineKeyboardMarkup(
    row_width=2,
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Нет', callback_data='do not subscribe'),
        ]

    ]
)

rubrics = ['Животные', 'Война', 'Ужасы']

ikb_choose_category = InlineKeyboardMarkup(row_width=2)

for rubric in rubrics:
    button = InlineKeyboardButton(text=rubric, callback_data=rubric)
    ikb_choose_category.insert(button)

ikb_choose_category.add(back_button)

