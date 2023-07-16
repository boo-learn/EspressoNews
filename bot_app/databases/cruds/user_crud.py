import logging
from typing import Optional, List

from bot_app.databases.repositories import UserRepository
from shared.models import User
logger = logging.getLogger(__name__)

class UserCRUD:
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
            if hasattr(settings, option):
                logging.info("Step 2")
                logging.info(f"Settings {settings}, option {option}, value {value}")
                return await self.repository.update_setting(settings, option, value)

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

