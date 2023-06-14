from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

channels = ['Канал 1', 'Канал 2', 'Канал 3']

ikb_my_channels = InlineKeyboardMarkup(row_width=2)

for channel in channels:
    button = InlineKeyboardButton(text=channel, callback_data=channel)
    ikb_my_channels.insert(button)

ikb_my_channels.add(InlineKeyboardButton(text='Добавить новый', callback_data='add new channel'))

# сделать пагинацию по 10 каналов