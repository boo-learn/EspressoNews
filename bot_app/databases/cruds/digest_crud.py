import logging
from typing import Optional, List, Tuple

from bot_app.databases.repositories import DigestRepository
from shared.config import DIGESTS_LIMIT
from shared.db_utils import get_user_settings

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

        user_settings = await get_user_settings(digest.user_id)

        if user_settings is None:
            return None

        user_role = user_settings.role_id
        user_intonation = user_settings.intonation_id

        summaries = []
        for post in digest.posts[offset:offset + limit]:
            for summary in post.summaries:
                if summary.role_id == user_role and summary.intonation_id == user_intonation:
                    if summary.content:
                        summaries.append(summary.content)

        total_count = len(digest.posts)
        return summaries, total_count
