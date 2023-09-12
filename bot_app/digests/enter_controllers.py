import logging
from typing import Optional, Tuple, List

import aiogram

from bot_app.core.messages.manager import AiogramMessageManager
from bot_app.core.types import base
from bot_app.digests.cruds import DigestCRUD

from bot_app.core.messages.senders import AbstractSender
from shared.config import DIGESTS_LIMIT

logger = logging.getLogger(__name__)


class NotificationMailingManager(base.MailingManager):
    def __init__(self):
        super().__init__()
        self.aiogram_message_manager = AiogramMessageManager(sender=AbstractSender())

    async def create_rule_for_all(
            self,
            task_name_template: str,
            task_func: str,
            cron_periodicity: str = None,
            setting_option: str = None
    ):
        await self._base_create_rule_for_all(
            task_name_template,
            task_func,
            cron_periodicity,
            setting_option,
        )

    async def create_rule(
            self,
            user_id: int,
            cron_periodicity: str,
            task_name_template: str,
            task_func: str
    ):
        await self._base_create_rule(
            user_id,
            cron_periodicity,
            task_name_template,
            task_func
        )

    def send(
            self,
            message_key,
    ):
        users = self.user_crud.get_all_users()

        for user in users:
            user_language_object = await self.user_crud.get_settings_option_for_user(user.user_id, 'language')
            self.aiogram_message_manager.set_language(user_language_object.code)

            try:
                await self.aiogram_message_manager.send_message(
                    message_key,
                    user.user_id,
                    name=user.first_name
                )
            except aiogram.exceptions.BotBlocked:
                await self.user_crud.disable_user(user.user_id)


class DigestMailingManager(base.MailingManager):
    def __init__(self):
        super().__init__()
        self.aiogram_message_manager = AiogramMessageManager(sender=AbstractSender())

    async def create_rule_for_all(
            self,
            task_name_template: str,
            task_func: str,
            cron_periodicity: str = None,
            setting_option: str = None
    ):
        await self._base_create_rule_for_all(
            task_name_template,
            task_func,
            cron_periodicity,
            setting_option,
        )

    async def create_rule(
            self,
            user_id: int,
            cron_periodicity: str,
            task_name_template: str,
            task_func: str
    ):
        await self._base_create_rule(
            user_id,
            cron_periodicity,
            task_name_template,
            task_func
        )

    @staticmethod
    async def fetch_and_format_digest(
            digest_id: int,
            offset: int = 0,
            limit: int = DIGESTS_LIMIT
    ):
        digest_crud = DigestCRUD()
        digest_summaries_list, total_count = await digest_crud.get_digest_summaries_by_id_and_count(
            digest_id=digest_id,
            offset=offset,
            limit=limit
        )
        logger.info(f'Digest count {total_count}')
        logger.info(f'Digests list counts {len(digest_summaries_list)}')

        return digest_summaries_list, total_count

    async def get_object_to_send_from_digest(
            self,
            digest_id,
            digests_limit,
            offset=0
    ):
        temp_result: Optional[Tuple[List[str], int]] = await self.fetch_and_format_digest(
            digest_id,
            offset,
            digests_limit
        )

        digest_summary_list, total_count = temp_result

        digest_message = '\n\n'.join(digest_summary_list[:DIGESTS_LIMIT])

        keyboard = None

        if total_count > digests_limit:
            digest_message += '\n\n' + self.aiogram_message_manager.get_message('digest_load_more')
            keyboard = 'digest_load_more'

        return {
            'message': digest_message,
            'keyboard': keyboard,
        }

    async def send(
            self,
            user_id: int,
            digest_id: int,
            offset: int = 0,
            limit: int = DIGESTS_LIMIT
    ):

        user_language_object = await self.user_crud.get_settings_option_for_user(user_id, 'language')
        self.aiogram_message_manager.set_language(user_language_object.code)

        message_object = await self.get_object_to_send_from_digest(digest_id, offset, limit)

        try:
            await self.aiogram_message_manager.send_message_in_parts(
                message_object['message'],
                user_id,
                message_object['keyboard'],
                dynamic_keyboard_parameters={
                    'digest_id': digest_id,
                    'offset': limit
                }
            )
        except aiogram.exceptions.BotBlocked:
            await self.user_crud.disable_user(user_id)
        else:
            digest_crud = DigestCRUD()
            digest = await digest_crud.repository.get(digest_id)
            await digest_crud.repository.change_digest(digest, user_id)

    async def not_exist(self, data):
        logger.info(f'Digest data {data}')

        user_language_object = await self.user_crud.get_settings_option_for_user(data['user_id'], 'language')

        self.aiogram_message_manager.set_language(user_language_object.code)

        try:
            await self.aiogram_message_manager.send_message('digest_not_exist', data["user_id"])
        except aiogram.exceptions.BotBlocked:
            await self.user_crud.disable_user(data["user_id"])


