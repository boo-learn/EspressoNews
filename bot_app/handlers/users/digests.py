import logging

from aiogram import types

from bot_app.data.messages import gen_digest_load_more
from bot_app.keyboards.inlines import ikb_load_more
from bot_app.loader import dp
from bot_app.logic.digest_logic_handler import DigestLogicHandler
from shared.config import DIGESTS_LIMIT

logger = logging.getLogger(__name__)


@dp.callback_query_handler(lambda c: True)
async def send_summaries_with_offset(call: types.CallbackQuery):
    logger.info(f'Handler send_summaries_with_offset called with data {call.data}')
    func_data = call.data.split('_')
    digest_id = int(func_data[-1])
    offset = int(func_data[-3])
    limit = offset + DIGESTS_LIMIT
    user_id = call.from_user.id

    logic_handler = DigestLogicHandler()
    digest_summary_list, total_count = await logic_handler.fetch_and_format_digest(digest_id, user_id, offset, limit)

    # Combine all digest summaries into a nicely formatted string
    digest_message = '\n\n'.join(digest_summary_list[:DIGESTS_LIMIT])

    if total_count > limit:
        # Add the load more message to the digest message
        digest_message += '\n\n' + gen_digest_load_more()
        reply_markup = ikb_load_more(digest_id, limit)
    else:
        reply_markup = None

    # Send the digest message in parts, if necessary
    await logic_handler.send_message_parts(
        send_method=lambda text, reply_markup=reply_markup: call.message.answer(
            text,
            disable_web_page_preview=True,
            reply_markup=reply_markup
        ),
        text=digest_message,
        max_length=4096,  # or any desired max_length
        reply_markup=reply_markup
    )


