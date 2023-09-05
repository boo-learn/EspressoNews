import logging
from typing import Optional, List

from bot_app.databases.repositories import UserRepository
from shared.db_utils import get_role, get_intonation, get_language
from shared.models import User
from datetime import datetime

logger = logging.getLogger(__name__)


class UserCRUD:
    settings_value_mappings = {
        'list_official': 'Official',
        'list_sarcastic-joking': 'Comedy_sarcastic',
        'list_announcer': 'Announcer',
        'list_standard': 'Helpfull assistant.',
        'list_every_hour': '0 */1 */1 */1 */1',
        'list_every_3_hours': '0 */3 */1 */1 */1',
        'list_every_6_hours': '0 */6 */1 */1 */1',
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
            'language_code': language_code,
            'is_active': False
        }

        if not user:
            user = await self.repository.create(**data)
        return user

    async def get_all_users(self) -> List[Optional[User]]:
        return await self.repository.get_all()

    async def update_user_settings_option(
            self,
            message_manager,
            user_id: int,
            option: str,
            value
    ) -> bool:
        if option == 'language':
            language = await get_language(value)
            return await self.repository.update_setting(user_id, option, language)

        updated_settings_value_mappings = {
            message_manager.get_message(key): value for key, value in UserCRUD.settings_value_mappings.items()
        }

        mapped_value = updated_settings_value_mappings[value]

        if option == 'role':
            role = await get_role(mapped_value)
            logging.info(f"Updating role setting with value: {role}")
            return await self.repository.update_setting(user_id, option, role)
        elif option == 'intonation':
            intonation = await get_intonation(mapped_value)
            logging.info(f"Updating intonation setting with value: {intonation}")
            return await self.repository.update_setting(user_id, option, intonation)
        else:
            logging.info(f"Updating setting {option} with value: {mapped_value}")
            return await self.repository.update_setting(user_id, option, mapped_value)

    async def get_settings_option_for_all_users(self, option_name: str):
        users_settings = await self.repository.get_all_users_settings()

        user_ids = []
        options = []

        for user_settings in users_settings:
            if hasattr(user_settings, option_name):
                user_ids.append(user_settings.user_id)
                options.append(getattr(user_settings, option_name))

        return user_ids, options

    # не правильное название функции
    async def get_settings_option_for_user(self, user_id: int, option_name: str):
        user_settings = await self.repository.get_user_settings(user_id)

        if hasattr(user_settings, option_name):
            return getattr(user_settings, option_name)

        return None

    async def get_all_user_settings(self, user_id: int):
        return await self.repository.get_user_settings(user_id)

    async def disable_user(self, user_id):
        user = await self.repository.get(user_id)
        await self.repository.update(user, is_active=False, disabled_at=datetime.now())
        await self.repository.update_setting(user_id, "periodicity", None)
        task_name = f"generate-digest-for-{str(user_id)}"
        await self.repository.delete_schedule(task_name)

    async def enable_user(self, user):
        await self.repository.update(user, is_active=True)
        await self.repository.update_setting(user.user_id, "periodicity", "*/1 * * * *")

    async def update_user_name(self, user_id: int, first_name: str):
        user = await self.repository.get(user_id)
        user = await self.repository.update(user, first_name=first_name)
        return user

    def get_language(self, param):
        pass
