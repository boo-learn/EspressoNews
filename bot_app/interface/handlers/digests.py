
import logging

from aiogram import types

from bot_app.core.users.crud import UserCRUD
from bot_app.loader import dp
from bot_app.core.tools.handler_tools import HandlersTools
from bot_app.digests.enter_controllers import DigestMailingManager
from shared.config import DIGESTS_LIMIT

logger = logging.getLogger(__name__)


class DigestsHandlers(HandlersTools):
    def __init__(self):
        super().__init__()
        self.register_handlers()
        self.user_crud = UserCRUD()
        self.mailing_manager = DigestMailingManager()

    def register_handlers(self):
        self.registrar.simply_handler_registration(
            dp.register_message_handler,
            self.send_summaries_with_offset,
            None,
            "always"
        )

    async def send_summaries_with_offset(self, call: types.CallbackQuery):
        logger.info(f'Handler send_summaries_with_offset called with data {call.data}')
        _, _, offset_str, _, _, digest_id_str = call.data.split('_')
        limit = int(offset_str) + DIGESTS_LIMIT

        await self.mailing_manager.send(call.from_user.id, int(digest_id_str), int(offset_str), limit)
