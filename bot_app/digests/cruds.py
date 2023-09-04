import logging
from typing import Optional, List, Tuple

from bot_app.databases.repositories import DigestRepository
from shared.config import DIGESTS_LIMIT

logger = logging.getLogger(__name__)


class DigestCRUD:
    def __init__(self):
        self.repository = DigestRepository()

    async def create_digest(self, user_id: int):
        await self.repository.create(user_id)

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
        post_number = 0  # + offset
        processed = []
        total_count = 0

        for post in digest.posts:
            if (post.channel.channel_id, post.post_id) in processed:
                total_count -= 1
                continue
            processed.append((post.channel.channel_id, post.post_id))
            post_number += 1
            if post_number - 1 < offset:
                continue
            if post_number > offset + limit:
                continue

            for summary in post.summaries:
                if summary.role_id == user_role and summary.intonation_id == user_intonation:
                    if summary.content:
                        summary_result = f"• {summary.content} <a href='https://t.me/{post.channel.channel_username}/{post.post_id}'> #{post_number} </a>"
                        summaries.append(summary_result)
                    else:
                        logger.warning("Summary content is empty")

        total_count += len(digest.posts)
        return summaries, total_count
