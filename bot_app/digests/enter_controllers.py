import logging
from typing import Optional, Tuple, List

import aiogram

from bot_app.digests.cruds import DigestCRUD

from bot_app.core.users.crud import UserCRUD
from bot_app.core.tools.handler_tools import HandlersTools
from bot_app.core.messages.senders import AbstractSender
from shared.config import DIGESTS_LIMIT
from shared.db_utils import update_or_create_schedule_in_db

logger = logging.getLogger(__name__)


class DigestMailingManager(HandlersTools):
    def __init__(self):
        super().__init__()
        self.user_crud = UserCRUD()

    async def create_rule_for_all(self):
        logger.info("Starting to create mail rules...")
        user_ids, users_list_periodicity_options = await self.user_crud.get_settings_option_for_all_users(
            'periodicity'
        )

        for user_id, option in zip(user_ids, users_list_periodicity_options):
            await self.create_rule(user_id, option)

        logger.info("Finished creating mail rules.")

    @staticmethod
    async def create_rule(user_id: int, periodicity_option: str):
        logger.info(f"Starting to create mail rule for user {user_id}...")
        logger.info(f"Got settings option for user {user_id}.")

        if periodicity_option is None:
            periodicity_option = '0 */1 */1 */1 */1'

        task_name = f'generate-digest-for-{str(user_id)}'
        task_schedule = {
            'task': 'tasks.generate_digest_for_user',
            'schedule': periodicity_option,
            'args': (user_id,),
        }
        logging.info(f"{task_schedule}")
        await update_or_create_schedule_in_db(task_name, task_schedule)
        logger.info(f"Finished creating mail rule for user {user_id}.")

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
        self.aiogram_message_manager.set_sender(AbstractSender())

        try:
            await self.aiogram_message_manager.send_message('digest_not_exist', data["user_id"])
        except aiogram.exceptions.BotBlocked:
            await self.user_crud.disable_user(data["user_id"])


