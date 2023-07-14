import logging
from typing import Optional, List, Tuple

from bot_app.databases.repositories import DigestRepository
from shared.config import DIGESTS_LIMIT

logger = logging.getLogger(__name__)


class DigestCRUD:
    def __init__(self):
        self.repository = DigestRepository()

    async def get_digest_summaries_by_id_and_count(
            self,
            digest_id: int,
            offset: int = 0,
            limit: int = DIGESTS_LIMIT
    ) -> Optional[Tuple[List[str], int]]:
        digest = await self.repository.get(digest_id)

        if digest is None:
            return None

        summaries = [post.summary for post in digest.posts[offset:offset + limit]]
        total_count = len(digest.posts)
        return summaries, total_count
