import logging
from typing import Optional, List

from bot_app.databases.repositories import UserRepository
from shared.db_utils import get_role, get_intonation
from shared.models import User
from shared.selection_values_for_models import PeriodicityEnum

logger = logging.getLogger(__name__)


class UserCRUD:
    settings_value_mappings = {
        'Официальная': 'Official',
        'Саркастично-шутливая': 'Comedy_sarcastic',
        'Диктор': 'Announcer',
        'Стандартная': 'Helpfull assistant.',
        'Каждый час': PeriodicityEnum.HOURLY,
        'Каждые 3 часа': PeriodicityEnum.EVERY_THREE_HOURS,
        'Каждые 6 часов': PeriodicityEnum.EVERY_SIX_HOURS,
    }

    def __init__(self):
        self.repository = UserRepository()

    async def check_user_and_create_if_none(
            self,
            user_id: int,
            username: str,
            first_name: str,
            last_name: str,
            language_code: str = 'ru'
    ) -> Optional[User]:
        user = await self.repository.get(user_id)

        data = {
            'user_id': user_id,
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
            'language_code': language_code
        }

        if not user:
            user = await self.repository.create(**data)

        return user

    async def get_all_users(self) -> List[Optional[User]]:
        return await self.repository.get_all()

    async def update_user_settings_option(
            self,
            user_id: int,
            option: str,
            value
    ) -> bool:
        user = await self.repository.get(user_id)

        if user:
            logging.info("Step 1")
            settings = user.settings
            logging.info(f"Settings: {settings}")
            logging.info(f"Option: {option}")
            if hasattr(settings, option):
                logging.info("Step 2")
                logging.info(f"Settings {settings}, option {option}, value {value}")
                mapped_value = UserCRUD.settings_value_mappings[value]

                if option == 'role':
                    role = await get_role(mapped_value)
                    logging.info(f"Updating role setting with value: {role}")
                    return await self.repository.update_setting(settings, option, role)
                elif option == 'intonation':
                    intonation = await get_intonation(mapped_value)
                    logging.info(f"Updating intonation setting with value: {intonation}")
                    return await self.repository.update_setting(settings, option, intonation)
                else:
                    logging.info(f"Updating setting {option} with value: {mapped_value}")
                    return await self.repository.update_setting(settings, option, mapped_value)

        return False

    async def get_settings_option_for_all_users(self, option_name: str):
        users_settings = await self.repository.get_all_users_settings()

        user_ids = []
        options = []

        for user_settings in users_settings:
            if hasattr(user_settings, option_name):
                user_ids.append(user_settings.user_id)
                options.append(getattr(user_settings, option_name))

        return user_ids, options

    async def get_settings_option_for_user(self, user_id: int, option_name: str):
        user_settings = await self.repository.get_user_settings(user_id)

        if hasattr(user_settings, option_name):
            return getattr(user_settings, option_name)

        return None
