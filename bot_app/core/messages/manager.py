import asyncio
import logging

from bot_app.core.messages.senders import AnswerSender, MessageSender
from bot_app.loader import bot
from bot_app.core.keyboards.generator import KeyboardGenerator
from bot_app.core.middlewares.i18n_middleware import i18n

logger = logging.getLogger(__name__)


class MessageManager:
    """
    Manages the sending of messages from different senders, taking into account the language of the user who gets from
    the cache
    """

    def __init__(self, sender=None):
        """
        Initializes a new MessageManager instance.

        :param sender: Optional message sender implementation.
        """
        self.lang_code = None
        self.message_obj = None
        self.sender = sender or AnswerSender()

    def _ensure_language_exists(self):
        if not self.lang_code:
            raise ValueError(f"language is not set!")

    def ensure_message_obj_exists(self):
        if not self.message_obj:
            raise ValueError(f"message_obj is not set!")

    def set_language(self, lang_code):
        self.lang_code = lang_code

    def set_message(self, message):
        self.message_obj = message

    def set_sender(self, sender: MessageSender):
        """
        Sets the message sender implementation.

        :param sender: The message sender instance.
        """
        self.sender = sender

    def get_message(self, message_key, **kwargs) -> str:
        """
        Gets a localized message based on the message key and user settings.

        :param message_key: The key for the message content.
        :param kwargs: Additional keyword arguments for message content formatting.
        :return: Localized message string.
        """
        self._ensure_language_exists()
        try:
            return i18n.gettext(
                singular=message_key,
                locale=self.lang_code
            ).format(**kwargs)
        except Exception as e:
            logger.warning(
                f'Exception while translating key "{message_key}": {e}. '
                f'Using the key as the message.')
            return message_key

    async def _get_reply_markup(self, key, dynamic_keyboard_parameters=None):
        logger.info(
            f'Семнадцатый шаг - генерация клавиатуры \n \n'
            f'{key} \n \n'
            f'{dynamic_keyboard_parameters} \n \n'
        )
        keyboard_generator = KeyboardGenerator()
        return await keyboard_generator.generate_keyboard(self, key, dynamic_keyboard_parameters)

    async def send_message(
        self,
        key,
        chat_id=None,
        dynamic_keyboard_parameters=None,
        off_preview=True,
        **message_kwargs
    ):
        """
        Sends a message using the set message sender.

        :param key: The key for the message content and keyboard.
        :param chat_id: Need for abstract sender.
        :param dynamic_keyboard_parameters: Array for dynamic create keyboard.
        :param off_preview: Optional flag to disable web page preview.
        :param message_kwargs: Additional keyword arguments for message content formatting.
        """
        logging.info(
            f'Пятнадцатый шаг - вторая проверка объекта сообщения \n \n'
            f'{self.lang_code} \n \n'
        )
        self._ensure_language_exists()
        logging.info(
            f'Шестнадцатый шаг - проверка  пройдена \n \n'
            f'{self.message_obj}'
        )
        reply_markup = await self._get_reply_markup(key, dynamic_keyboard_parameters)
        logger.info(
            f'23 шаг - клавиатура готова \n \n'
            f'{reply_markup} \n \n'
        )
        await self.sender.send(
            self,
            key,
            chat_id,
            reply_markup,
            off_preview,
            **message_kwargs
        )

    async def send_message_in_parts(
            self,
            text,
            chat_id,
            keyboard=None,
            dynamic_keyboard_parameters=None,
            max_length=4096
    ):
        text_parts = [text[i:i + max_length] for i in range(0, len(text), max_length)]

        if keyboard:
            keyboard = await self._get_reply_markup(keyboard, dynamic_keyboard_parameters)

        for i, text_part in enumerate(text_parts):
            is_last_message = i == len(text_parts) - 1
            keyboard = keyboard if is_last_message else None

            await bot.send_message(
                chat_id=chat_id,
                text=text_part,
                disable_web_page_preview=True,
                reply_markup=keyboard
            )

            await asyncio.sleep(1)

    async def delete_before_message(self):
        """
        Deletes the previous message in the chat.
        """
        await bot.delete_message(
            chat_id=self.message_obj.chat.id,
            message_id=self.message_obj.message_id - 1
        )

    async def delete_message_before_last(self):
        """
        Deletes the previous + previous message in the chat.
        """
        await bot.delete_message(
            chat_id=self.message_obj.chat.id,
            message_id=self.message_obj.message_id - 2
        )
