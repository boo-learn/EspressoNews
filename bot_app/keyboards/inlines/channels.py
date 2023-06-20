from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot_app.keyboards.inlines.back import back_button


def get_choose_channels_ikb(subscribed_channels):
    ikb_my_channels = InlineKeyboardMarkup(row_width=2)
    for channel in subscribed_channels:
        channel_button = InlineKeyboardButton(
            text=channel.channel_name, callback_data=f"choose_channel_{channel.channel_username}"
        )
        ikb_my_channels.insert(channel_button)

    return ikb_my_channels


def get_sure_unsubscribe_ikb():
    ikb_unsubscribe = InlineKeyboardMarkup(
        row_width=2,
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Да', callback_data='unsubscribe'),
                InlineKeyboardButton(text='Нет', callback_data='do not unsubscribe'),
            ]

        ]
    )

    return ikb_unsubscribe


def get_sure_subscribe_ikb(channel_username):
    ikb_subscribe = InlineKeyboardMarkup(
        row_width=2,
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Отписаться', callback_data=f'do not subscribe&slash&{channel_username}')
            ]

        ]
    )

    return ikb_subscribe


def get_posts_rubrics(rubrics=None):
    if rubrics is None:
        rubrics = ['Животные', 'Война', 'Ужасы']

    ikb_choose_category = InlineKeyboardMarkup(row_width=2)

    for rubric in rubrics:
        button = InlineKeyboardButton(text=rubric, callback_data=rubric)
        ikb_choose_category.insert(button)

    ikb_choose_category.add(back_button)

    return ikb_choose_category


