import logging
from typing import Optional, List, Tuple

from bot_app.databases.repositories import DigestRepository
from shared.config import DIGESTS_LIMIT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DigestCRUD:
    def __init__(self):
        self.repository = DigestRepository()

    async def get_digest_summaries_by_id_and_count(
            self,
            digest_id: int,
            user_id: int,
            offset: int = 0,
            limit: int = DIGESTS_LIMIT
    ) -> Optional[Tuple[List[str], int]]:
        digest = await self.repository.get(digest_id)

        if digest is None:
            logger.warning(f"Digest with ID: {digest_id} not found")
            return None

        user_role = digest.role_id
        user_intonation = digest.intonation_id

        logger.info(f"Digest details - User role ID: {user_role}, User intonation ID: {user_intonation}")

        summaries = []
        post_number = 1 + offset

        # Логирование деталей постов в дайджесте
        for post in digest.posts:
            logger.info(f"Post details - ID: {post.post_id}, channel ID: {post.channel.channel_id}, channel username: {post.channel.channel_username}")

        for post in digest.posts[offset:offset + limit]:
            logger.info(f"Processing post number: {post_number}, post ID: {post.post_id}")
            for summary in post.summaries:
                if summary.role_id == user_role and summary.intonation_id == user_intonation:
                    if summary.content:
                        summary_result = f"• {summary.content} <a href='https://t.me/{post.channel.channel_username}/{post.post_id}'> #{post_number} </a>"
                        summaries.append(summary_result)
                        logger.info(f"Added summary: {summary_result} for post ID: {post.post_id}, channel ID: {post.channel.channel_id}")
                    else:
                        logger.warning(f"Summary content is empty for post ID: {post.post_id}, channel ID: {post.channel.channel_id}")
            post_number += 1

        total_count = len(digest.posts)
        logger.info(f"Total posts count in digest: {total_count}")
        return summaries, total_count
