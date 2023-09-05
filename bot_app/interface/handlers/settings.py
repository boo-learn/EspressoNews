from aiogram import types

from bot_app.core.users.crud import UserCRUD
from bot_app.loader import dp
from bot_app.core.tools.handler_tools import HandlersTools

from bot_app.digests.enter_controllers import DigestMailingManager


class SettingsHandlers(HandlersTools):
    def __init__(self):
        super().__init__()
        self.register_routes()
        self.user_crud = UserCRUD()
        self.mailing_manager = DigestMailingManager()

    def register_routes(self):
        self.aiogram_registrar.multilingual_handler_registration(
            dp.register_message_handler,
            self.return_in_menu,
            'regexp_main_menu',
            'regexp'
        )
        self.aiogram_registrar.multilingual_handler_registration(
            dp.register_message_handler,
            self.change_periodicity_option,
            'regexp_periodicity',
            'regexp'
        )
        self.aiogram_registrar.multilingual_handler_registration(
            dp.register_message_handler,
            self.change_intonation_option,
            'regexp_intonation',
            'regexp'
        )
        self.aiogram_registrar.multilingual_handler_registration(
            dp.register_message_handler,
            self.change_role_option,
            'regexp_role',
            'regexp'
        )
        self.aiogram_registrar.multilingual_handler_registration(
            dp.register_message_handler,
            self.change_language_option,
            'regexp_language',
            'regexp'
        )
        self.aiogram_registrar.multilingual_handler_registration(
            dp.register_message_handler,
            self.success_change_intonation_option,
            ['list_official', 'list_sarcastic-joking'],
            "in_list"
        )
        self.aiogram_registrar.multilingual_handler_registration(
            dp.register_message_handler,
            self.success_change_periodicity_option,
            ['list_every_hour', 'list_every_3_hours', 'list_every_6_hours'],
            "in_list"
        )
        self.aiogram_registrar.multilingual_handler_registration(
            dp.register_message_handler,
            self.success_change_role_option,
            ['list_announcer', 'list_standard'],
            "in_list"
        )
        self.aiogram_registrar.simply_handler_registration(
            dp.register_message_handler,
            self.success_change_language,
            ['中文', 'Español', 'English', 'हिन्दी', 'العربية', 'বাংলা', 'পর্তুগিজ', 'Русский', '日本語'],
            "in_list"
        )

    async def return_in_menu(self, message: types.Message):
        await self.aiogram_message_manager.send_message('menu')

    async def change_periodicity_option(self, message: types.Message):
        await self.aiogram_message_manager.send_message('change_option_periodicity')

    async def change_intonation_option(self, message: types.Message):
        await self.aiogram_message_manager.send_message('change_option_intonation')

    async def change_role_option(self, message: types.Message):
        await self.aiogram_message_manager.send_message('change_option_role')

    async def change_language_option(self, message: types.Message):
        await self.aiogram_message_manager.send_message('change_option_language')

    async def success_change_intonation_option(self, message: types.Message):
        await self.user_crud.update_user_settings_option(
            self.aiogram_message_manager,
            message.from_user.id,
            'intonation',
            message.text
        )
        await self.aiogram_message_manager.send_message('settings_save_success')

    async def success_change_periodicity_option(self, message: types.Message):
        await self.user_crud.update_user_settings_option(
            self.aiogram_message_manager,
            message.from_user.id,
            'periodicity',
            message.text
        )

        periodicity_option = await self.user_crud.get_settings_option_for_user(message.from_user.id, 'periodicity')
        await self.mailing_manager.create_rule(message.from_user.id, periodicity_option)
        await self.aiogram_message_manager.send_message('settings_save_success')

    async def success_change_role_option(self, message: types.Message):
        await self.user_crud.update_user_settings_option(
            self.aiogram_message_manager,
            message.from_user.id,
            'role',
            message.text
        )
        await self.aiogram_message_manager.send_message('settings_save_success')

    async def success_change_language(self, message: types.Message):
        await self.user_crud.update_user_settings_option(
            self.aiogram_message_manager,
            message.from_user.id,
            'language',
            message.text
        )
        language_option = await self.user_crud.get_settings_option_for_user(
            message.from_user.id,
            'language'
        )

        self.aiogram_message_manager.set_language(language_option.code)
        await self.aiogram_message_manager.send_message('settings_save_success')
        await self.aiogram_message_manager.send_message('menu')
