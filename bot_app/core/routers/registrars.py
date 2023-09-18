import logging
import re

from bot_app.core.middlewares.i18n_middleware import i18n

from aiogram.dispatcher.filters import Command

from bot_app.core.types import base
from shared.config import RABBIT_HOST
from shared.rabbitmq import Subscriber, QueuesType

logger = logging.getLogger(__name__)


class AiogramRoutesRegistrar:
    """
    This class serves as a registrar for routers in aiogram.
    It provides utilities for simple as well as multilingual handler registrations.
    """

    def __init__(self):
        """
        Initialize the registration functions for various handler types.
        """
        self.registration_functions = {
            "command": (
                self.get_translated_pattern,
                lambda aiogram_register_func, func, pattern, state: aiogram_register_func(
                    func,
                    Command(pattern),
                    state=state
                )
            ),
            "regexp": (
                self.get_translated_pattern,
                lambda aiogram_register_func, func, pattern, state: aiogram_register_func(
                    func,
                    regexp=re.compile(f"^{pattern}$", re.IGNORECASE),
                    state=state
                )
            ),
            "in_list": (
                self.get_translated_list,
                lambda aiogram_register_func, func, list_, state: aiogram_register_func(
                    func,
                    lambda message: message.text in list_,
                    state=state
                )
            ),
            "text": (
                self.get_translated_pattern,
                lambda aiogram_register_func, func, pattern, state: aiogram_register_func(
                    func,
                    text=pattern,
                    state=state
                )
            ),
            "text_contains": (
                self.get_translated_pattern,
                lambda aiogram_register_func, func, pattern, state: aiogram_register_func(
                    func,
                    text_contains=pattern,
                    state=state
                )
            ),
            "content_types": (
                lambda x, y: None,
                lambda aiogram_register_func, func, content_type, state: aiogram_register_func(
                    func,
                    content_types=content_type,
                    state=state
                )
            ),
            "only_state": (
                lambda x, y: None,
                lambda aiogram_register_func, func, _, state: aiogram_register_func(
                    func,
                    state=state
                )
            ),
            "always": (
                lambda x, y: None,
                lambda aiogram_register_func, func, _, state: aiogram_register_func(func, state=state)
            )
        }

    def simply_handler_registration(
            self,
            aiogram_register_func,
            handler,
            pattern_or_list,
            handler_type,
            state=None
    ):
        """
        Perform a straightforward handler registration.

        :param aiogram_register_func: The aiogram function to register the handler.
        :param handler: The handler function.
        :param pattern_or_list: The pattern or list for filtering.
        :param handler_type: The type of the handler.
        :param state: The state for the handler (default is None).
        """
        _, register_func = self.registration_functions[handler_type]
        register_func(aiogram_register_func, handler, pattern_or_list, state)

    def multilingual_handler_registration(
            self,
            aiogram_register_func,
            handler,
            pattern_or_list,
            handler_type,
            state=None
    ):
        """
        Register routers for multilingual commands.

        :param aiogram_register_func: The aiogram function to register the handler.
        :param handler: The handler function.
        :param pattern_or_list: The pattern or list for filtering.
        :param handler_type: The type of the handler.
        :param state: The state for the handler (default is None).
        """
        translate_func, register_func = self.registration_functions[handler_type]

        lang_codes = ['ar', 'bn', 'en', 'es', 'hi', 'ja', 'pt', 'ru', 'zh']
        for code in lang_codes:
            translated_data = translate_func(pattern_or_list, code)
            register_func(aiogram_register_func, handler, translated_data, state)

    @staticmethod
    def get_translated_pattern(pattern, code):
        """
        Return translated pattern for a specific language.

        :param pattern: The pattern to be translated.
        :param code: The language code for translation.
        :return: Translated pattern string.
        """
        return i18n.gettext(singular=pattern, locale=code)

    @staticmethod
    def get_translated_list(list_, code):
        """
        Return a list of translated items for a specific language.

        :param list_: The list to be translated.
        :param code: The language code for translation.
        :return: List of translated items.
        """
        return [i18n.gettext(singular=item, locale=code) for item in list_]


class RabbitMQRoutesRegistrar:
    def __init__(self):
        self.recipient = None
        self.queue_name = None

    def _set_recipient(self):
        self.recipient = Subscriber(host=RABBIT_HOST, queue=QueuesType[self.queue_name])

    def _ensure_queue_name_exists(self):
        if not self.queue_name:
            raise ValueError(f"Queue_name is not set!")

    def set_queue_name(self, queue_name):
        self.queue_name = queue_name
        self._set_recipient()

    async def register_message_handler(self, message_key, callback_endpoint):
        self._ensure_queue_name_exists()
        self.recipient.subscribe(message_type=message_key, callback=callback_endpoint)
        await self.recipient.run()


# class RabbitMQRouterRegistry:
#     _routers = []
#
#     @classmethod
#     def register_router(cls, router: base.Router):
#         cls._routers.append(router)
#
#     @classmethod
#     def get_all_routers(cls):
#         return cls._routers
