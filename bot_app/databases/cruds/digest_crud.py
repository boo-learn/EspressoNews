import logging
from typing import Optional, List, Tuple

from bot_app.databases.repositories import DigestRepository
from shared.config import DIGESTS_LIMIT
from shared.loggers import get_logger


logger = get_logger('bot.db.crud.digest')


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
        digest_logger = logger.bind(digest_id=digest_id)
        digest = await self.repository.get(digest_id)

        if digest is None:
            digest_logger.warning("Digest not found")
            return None

        user_role = digest.role_id
        user_intonation = digest.intonation_id

        digest_logger.info("Digest details obtained", role_id=user_role, intonation_id=user_intonation)

        summaries = []
        post_number = 0  # + offset
        processed = []
        total_count = 0

        for post in digest.posts:
            post_logger = digest_logger.bind(channel=post.channel.channel_username, post_id=post.post_id)
            if (post.channel.channel_id, post.post_id) in processed:
                total_count -= 1
                continue
            processed.append((post.channel.channel_id, post.post_id))
            post_number += 1
            if post_number - 1 < offset:
                continue
            if post_number > offset + limit:
                break

            post_logger.info(f'Processing #{post_number} post')
            for summary in post.summaries:
                if summary.role_id == user_role and summary.intonation_id == user_intonation:
                    if summary.content:
                        summary_result = f"• {summary.content} <a href='https://t.me/{post.channel.channel_username}/{post.post_id}'> #{post_number} </a>"
                        summaries.append(summary_result)
                        logger.info("Added summary", summary=summary_result)
                    else:
                        logger.warning("Summary content is empty")

        total_count += len(digest.posts)
        digest_logger.info("Done with digest", post_count=total_count)
        return summaries, total_count
