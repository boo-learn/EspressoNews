from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot_app.keyboards.inlines.back import back_button

rubrics = ['Животные', 'Война', 'Ужасы']

ikb_choose_category = InlineKeyboardMarkup(row_width=2)

for rubric in rubrics:
    button = InlineKeyboardButton(text=rubric, callback_data=rubric)
    ikb_choose_category.insert(button)

ikb_choose_category.add(back_button)

