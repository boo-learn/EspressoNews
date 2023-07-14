from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def ikb_load_more(digest_id, offset):
    ikb_load_more_object = InlineKeyboardMarkup(
        row_width=1,
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='Далее',
                    callback_data=f'send_summaries_with_offset_{offset}_for_{digest_id}')
            ]

        ]
    )

    return ikb_load_more_object
