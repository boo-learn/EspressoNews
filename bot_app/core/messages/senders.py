import logging

from bot_app.core.types import base
from bot_app.loader import bot

logger = logging.getLogger(__name__)


class AbstractSender(base.AiogramMessageSender):
    async def send(
            self,
            aiogram_message_manager,
            message_key,
            chat_id=None,
            reply_markup=None,
            off_preview=True,
            **message_kwargs
    ):
        message = aiogram_message_manager.get_message(message_key, **message_kwargs)
        await bot.send_message(
            chat_id=chat_id,
            text=message,
            disable_web_page_preview=off_preview,
            reply_markup=reply_markup
        )
        logger.debug(f'{message_key} message sent')


class AnswerSender(base.AiogramMessageSender):
    """
    Message sender implementation using 'answer' method.
    """

    async def send(
            self,
            aiogram_message_manager,
            message_key,
            chat_id=None,
            reply_markup=None,
            off_preview=True,
            **message_kwargs
    ):
        """
        Sends a message using the 'answer' method.

        :param aiogram_message_manager: The AiogramMessageManager instance.
        :param message_key: The key for the message content.
        :param chat_id: No need. None.
        :param reply_markup: Optional reply markup for the message.
        :param off_preview: Optional flag to disable web page preview.
        :param message_kwargs: Additional keyword arguments for message content formatting.
        """
        aiogram_message_manager.ensure_message_obj_exists()

        message = aiogram_message_manager.get_message(message_key, **message_kwargs)

        await aiogram_message_manager.message_obj.answer(
            message,
            disable_web_page_preview=off_preview,
            reply_markup=reply_markup
        )


class ReplySender(base.AiogramMessageSender):
    """
    Message sender implementation using the 'reply' method.
    """

    async def send(
            self,
            aiogram_message_manager,
            message_key,
            chat_id=None,
            reply_markup=None,
            off_preview=True,
            **message_kwargs
    ):
        """
        Sends a reply message using the 'reply' method.

        :param aiogram_message_manager: The AiogramMessageManager instance.
        :param message_key: The key for the message content.
        :param chat_id: No need. None.
        :param reply_markup: Optional reply markup for the message.
        :param off_preview: Optional flag to disable web page preview.
        :param message_kwargs: Additional keyword arguments for message content formatting.
        """
        aiogram_message_manager.ensure_message_obj_exists()

        message = aiogram_message_manager.get_message(message_key, **message_kwargs)
        await aiogram_message_manager.message_obj.reply(
            message,
            disable_web_page_preview=off_preview,
            reply_markup=reply_markup
        )
        logger.debug(f'{message_key} reply sent')

