import logging

from bot_app.databases.repositories import DigestRepository

logger = logging.getLogger(__name__)


class DigestCRUD:
    def __init__(self):
        self.repository = DigestRepository()

    async def get_digest_summary_by_id(self, digest_id: int):
        digest = await self.repository.get(digest_id)
        return digest.total_summary
