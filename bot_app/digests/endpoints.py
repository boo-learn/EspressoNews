import logging

from bot_app.core.tools.handler_tools import HandlersTools
from bot_app.core.users.crud import UserCRUD
from bot_app.digests.enter_controllers import DigestMailingManager

logger = logging.getLogger(__name__)


class DigestRouter():
    def __init__(self):
        super().__init__()
        self.user_crud = UserCRUD()
        self.mailing_manager = DigestMailingManager()

    async def send(self, data: dict):
        logger.info(f'Digest trying send')
        logger.info(f'Digest data {data}')
        user_id = data['user_id']

        await self.mailing_manager.send(user_id, data['digest_id'])

    async def not_exist(self, data: dict):
        await self.mailing_manager.not_exist(data)
