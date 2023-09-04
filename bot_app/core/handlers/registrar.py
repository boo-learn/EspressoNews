import logging
import re

from bot_app.core.middlewares.i18n_middleware import i18n

from aiogram.dispatcher.filters import Command


logger = logging.getLogger(__name__)


class HandlerRegistrar:
    """
    This class serves as a registrar for handlers in aiogram.
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
        Register handlers for multilingual commands.

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
