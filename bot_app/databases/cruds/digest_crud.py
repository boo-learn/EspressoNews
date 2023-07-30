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

        user_role = digest.role_id
        user_intonation = digest.intonation_id

        summaries = []
        post_number = 1 + offset
        for post in digest.posts[offset:offset + limit]:
            for summary in post.summaries:
                if summary.role_id == user_role and summary.intonation_id == user_intonation:
                    if summary.content:
                        summary_result = f"• {summary.content} <a href='https://t.me/{post.channel.channel_username}/{post.post_id}'> #{post_number} </a>"
                        summaries.append(summary_result)
            post_number += 1

        total_count = len(digest.posts)
        return summaries, total_count
