import logging

from aiogram import types

from bot_app.data.messages import gen_digest_load_more
from bot_app.keyboards.inlines import ikb_load_more
from bot_app.loader import dp
from bot_app.logic.digest_logic_handler import DigestLogicHandler
from shared.config import DIGESTS_LIMIT

logger = logging.getLogger(__name__)


@dp.callback_query_handler(text_contains='send_summaries_with_offset_')
async def send_summaries_with_offset(call: types.CallbackQuery):
    func_data = call.data.split('_')
    digest_id = int(func_data[-1])
    offset = int(func_data[-3])
    limit = offset + DIGESTS_LIMIT

    logic_handler = DigestLogicHandler()
    digest_summary, total_count = await logic_handler.fetch_and_format_digest(digest_id, offset, limit)

    await logic_handler.send_message_parts(call.message.answer, digest_summary)

    await logic_handler.send_load_more(call.message.answer, total_count, digest_id, offset + DIGESTS_LIMIT)
