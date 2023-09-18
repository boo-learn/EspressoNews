import asyncio
import logging

import aiogram

from bot_app.core.messages.senders import AnswerSender
from bot_app.core.types import base
from bot_app.loader import bot
from bot_app.core.keyboards.generator import KeyboardGenerator
from bot_app.core.middlewares.i18n_middleware import i18n
from shared.config import RETRY_LIMIT, RABBIT_HOST
from shared.rabbitmq import QueuesType, Producer, MessageData

logger = logging.getLogger(__name__)


class AiogramMessageManager(base.MailingManager):
    """
    Manages the sending of messages from different senders, taking into account the language of the user who gets from
    the cache
    """

    def __init__(self, sender=None):
        """
        Initializes a new AiogramMessageManager instance.

        :param sender: Optional message sender implementation.
        """
        super().__init__()
        self.lang_code = None
        self.message_obj = None
        self.sender = sender or AnswerSender()

    async def create_rule_for_all(
            self,
            task_name_template: str,
            task_func: str,
            cron_periodicity: str = None,
            setting_option: str = None
    ):
        await self._base_create_rule_for_all(
            task_name_template,
            task_func,
            cron_periodicity,
            setting_option,
        )

    async def create_rule(
            self,
            user_id: int,
            cron_periodicity: str,
            task_name_template: str,
            task_func: str
    ):
        await self._base_create_rule(
            user_id,
            cron_periodicity,
            task_name_template,
            task_func
        )

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

    def set_sender(self, sender: base.AiogramMessageSender):
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
        self._ensure_language_exists()

        reply_markup = await self._get_reply_markup(key, dynamic_keyboard_parameters)

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

            for _ in range(RETRY_LIMIT):
                try:
                    await bot.send_message(
                        chat_id=chat_id,
                        text=text_part,
                        disable_web_page_preview=True,
                        reply_markup=keyboard
                    )
                except aiogram.exceptions.RetryAfter as error:
                    await asyncio.sleep(error.timeout)
                else:
                    break
            else:
                logger.info(f'Failed to send digest after {RETRY_LIMIT} retries')

            await asyncio.sleep(1)

    async def send_notification(
            self,
            message_key,
    ):
        users_params = await self.user_crud.get_all_user_id_and_first_name()

        logger.info(
            'Пользователей получил',
            f'{users_params}'
        )

        if not users_params:
            return False

        for user_id, first_name in users_params:
            user_language_object = await self.user_crud.get_settings_option_for_user(user_id, 'language')
            self.set_language(user_language_object.code)

            try:
                await self.send_message(
                    message_key,
                    user_id,
                    name=first_name
                )
            except aiogram.exceptions.BotBlocked:
                await self.user_crud.disable_user(user_id)

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


class RabbitMQMessageManager:
    def __init__(self):
        self.sender = None
        self.queue_name = None

    def _set_sender(self):
        self.sender = Producer(host=RABBIT_HOST, queue=QueuesType[self.queue_name])

    def _ensure_queue_name_exists(self):
        if not self.queue_name:
            raise ValueError(f"Queue_name is not set!")

    def set_queue_name(self, queue_name):
        self.queue_name = queue_name
        self._set_sender()

    async def send_message(self, message: MessageData, queue_name):
        self._ensure_queue_name_exists()
        await self.sender.send_message(message_with_data=message, queue=QueuesType[queue_name])
        # Поменять блять producer так, чтобы в нём использовался общий queue_name, а не приходилось передавать
        # в двух местах

