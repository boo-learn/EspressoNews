import asyncio
import logging

from bot_app.data.messages import gen_digest_load_more
from bot_app.databases.cruds import DigestCRUD
from bot_app.keyboards.inlines import ikb_load_more
from shared.config import DIGESTS_LIMIT

logger = logging.getLogger(__name__)


class DigestLogicHandler:
    @staticmethod
    async def fetch_and_format_digest(digest_id: int, offset: int = 0, limit: int = DIGESTS_LIMIT):
        digest_crud = DigestCRUD()
        digest_summaries_list, total_count = await digest_crud.get_digest_summaries_by_id_and_count(
            digest_id=digest_id,
            offset=offset,
            limit=limit
        )
        logger.info(f'Digest count {total_count}')
        logger.info(f'Digests list counts {len(digest_summaries_list)}')

        # Возвращаем список дайджестов, а не одну большую строку
        return digest_summaries_list, total_count

    @staticmethod
    async def send_message_parts(send_method, text, max_length=4096):
        for i in range(0, len(text), max_length):
            text_to_send = text[i:i + max_length]
            await send_method(text=text_to_send)
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
