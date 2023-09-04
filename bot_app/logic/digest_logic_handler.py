import asyncio
import logging
import aiogram

from bot_app.data.messages import gen_digest_load_more
from bot_app.databases.cruds import DigestCRUD
from bot_app.keyboards.inlines import ikb_load_more
from shared.config import DIGESTS_LIMIT, RETRY_LIMIT
from shared.loggers import get_logger

logger = get_logger('bot.digest.logic')


class DigestLogicHandler:
    @staticmethod
    async def fetch_and_format_digest(digest_id: int, user_id: int, offset: int = 0, limit: int = DIGESTS_LIMIT):
        digest_crud = DigestCRUD()
        digest_summaries_list, total_count = await digest_crud.get_digest_summaries_by_id_and_count(
            digest_id=digest_id,
            user_id=user_id,
            offset=offset,
            limit=limit
        )
        logger.info(f'Digest count {total_count}')
        logger.info(f'Digests list counts {len(digest_summaries_list)}')

        # Возвращаем список дайджестов, а не одну большую строку
        return digest_summaries_list, total_count

    @staticmethod
    async def send_message_parts(send_method, text, max_length=4096, reply_markup=None):
        text_parts = [text[i:i + max_length] for i in range(0, len(text), max_length)]
        for i, text_part in enumerate(text_parts):
            is_last_message = i == len(text_parts) - 1
            markup = reply_markup if is_last_message else None
            for _ in range(RETRY_LIMIT):
                try:
                    await send_method(text=text_part, reply_markup=markup)
                except aiogram.exceptions.RetryAfter as error:
                    logger.warning('Limit reached', error=error)
                    await asyncio.sleep(error.timeout)
                else:
                    break
            else:
                logger.error(f'Failed to send digest after {RETRY_LIMIT} retries')
            await asyncio.sleep(1)

    @staticmethod
    async def send_load_more(send_method, total_count: int, digest_id: int, offset: int):
        if total_count > DIGESTS_LIMIT:
            logger.info(f'Load more button send')
            reply_markup = ikb_load_more(digest_id=digest_id, offset=offset)
            logger.info(f'Load more button send {reply_markup} with offset {offset} and digest_id {digest_id}')
            await send_method(
                text=gen_digest_load_more(),
                reply_markup=reply_markup
            )
