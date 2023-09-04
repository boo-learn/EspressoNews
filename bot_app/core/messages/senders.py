import logging
from abc import ABC, abstractmethod

from bot_app.loader import bot

logger = logging.getLogger(__name__)


class MessageSender(ABC):
    """
    Abstract base class for message senders.
    """

    @abstractmethod
    async def send(
            self,
            message_manager,
            message_key,
            chat_id=None,
            reply_markup=None,
            off_preview=True,
            **message_kwargs
    ):
        """
        Sends a message using the specific message sender implementation.

        :param message_manager: The MessageManager instance.
        :param message_key: The key for the message content.
        :param chat_id: Need for abstract sender.
        :param reply_markup: Optional reply markup for the message.
        :param off_preview: Optional flag to disable web page preview.
        :param message_kwargs: Additional keyword arguments for message content formatting.
        """
        pass


class AbstractSender(MessageSender):
    async def send(
            self,
            message_manager,
            message_key,
            chat_id=None,
            reply_markup=None,
            off_preview=True,
            **message_kwargs
    ):
        message = message_manager.get_message(message_key, **message_kwargs)
        await bot.send_message(
            chat_id=chat_id,
            text=message,
            disable_web_page_preview=off_preview,
            reply_markup=reply_markup
        )
        logger.debug(f'{message_key} message sent')


class AnswerSender(MessageSender):
    """
    Message sender implementation using 'answer' method.
    """

    async def send(
            self,
            message_manager,
            message_key,
            chat_id=None,
            reply_markup=None,
            off_preview=True,
            **message_kwargs
    ):
        """
        Sends a message using the 'answer' method.

        :param message_manager: The MessageManager instance.
        :param message_key: The key for the message content.
        :param chat_id: No need. None.
        :param reply_markup: Optional reply markup for the message.
        :param off_preview: Optional flag to disable web page preview.
        :param message_kwargs: Additional keyword arguments for message content formatting.
        """
        message_manager.ensure_message_obj_exists()

        message = message_manager.get_message(message_key, **message_kwargs)
        logger.info(
            f'25 шаг - Смотрим само переведённое сообщение \n \n'
            f'{message} \n \n'
        )
        await message_manager.message_obj.answer(
            message,
            disable_web_page_preview=off_preview,
            reply_markup=reply_markup
        )


class ReplySender(MessageSender):
    """
    Message sender implementation using the 'reply' method.
    """

    async def send(
            self,
            message_manager,
            message_key,
            chat_id=None,
            reply_markup=None,
            off_preview=True,
            **message_kwargs
    ):
        """
        Sends a reply message using the 'reply' method.

        :param message_manager: The MessageManager instance.
        :param message_key: The key for the message content.
        :param chat_id: No need. None.
        :param reply_markup: Optional reply markup for the message.
        :param off_preview: Optional flag to disable web page preview.
        :param message_kwargs: Additional keyword arguments for message content formatting.
        """
        message_manager.ensure_message_obj_exists()

        message = message_manager.get_message(message_key, **message_kwargs)
        await message_manager.message_obj.reply(
            message,
            disable_web_page_preview=off_preview,
            reply_markup=reply_markup
        )
        logger.debug(f'{message_key} reply sent')
