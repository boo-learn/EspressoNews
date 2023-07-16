import re

from aiogram import types

from bot_app.databases.cruds import UserCRUD
from bot_app.keyboards.default import kb_menu, get_kb_periodicity, get_kb_intonation, get_kb_role
from bot_app.loader import dp
from bot_app.utils.create_mail_rules import create_mail_rule


@dp.message_handler(regexp=re.compile(r'^Главное меню$', re.IGNORECASE))
async def return_in_menu(message: types.Message):
    await message.answer('Главное меню', reply_markup=kb_menu)


@dp.message_handler(regexp=re.compile(r'^Периодичность$', re.IGNORECASE))
async def change_setting_periodicity(message: types.Message):
    await message.answer('Периодичность', reply_markup=get_kb_periodicity())


@dp.message_handler(regexp=re.compile(r'^Интонация$', re.IGNORECASE))
async def change_setting_intonation(message: types.Message):
    await message.answer('Интонация', reply_markup=get_kb_intonation())


@dp.message_handler(regexp=re.compile(r'^Роль$', re.IGNORECASE))
async def change_setting_role(message: types.Message):
    await message.answer('Роль', reply_markup=get_kb_role())


@dp.message_handler(
    lambda message: message.text in [
        'Официальная',
        'Саркастично-шутливая',
    ]
)
async def change_intonation_option(message: types.Message):
    user_crud = UserCRUD()
    await user_crud.update_user_settings_option(message.from_user.id, 'intonation', message.text)
    await message.answer('Изменения успешно сохранены!')


@dp.message_handler(
    lambda message: message.text in [
        'Каждый час',
        'Каждые 3 часа',
        'Каждые 6 часов',
    ]
)
async def change_periodicity_option(message: types.Message):
    user_crud = UserCRUD()
    await user_crud.update_user_settings_option(message.from_user.id, 'periodicity', message.text)
    await create_mail_rule(message.from_user.id)  # Add this line to call create_mail_rule
    await message.answer('Изменения успешно сохранены!')


@dp.message_handler(
    lambda message: message.text in [
        'Диктор',
    ]
)
async def change_role_option(message: types.Message):
    user_crud = UserCRUD()
    await user_crud.update_user_settings_option(message.from_user.id, 'role', message.text)
    await message.answer('Изменения успешно сохранены!')
