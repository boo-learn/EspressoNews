from __future__ import annotations

import logging

from bot_app.core.keyboards.registrar import KeyboardRegistry


logger = logging.getLogger(__name__)


class KeyboardGenerator:
    """
    A class responsible for generating keyboards, translating button texts, and retrieving button data.

    """

    def __init__(self) -> None:
        """
        Initializes a new instance of the KeyboardGenerator.
        """
        self.keyboard_registry = KeyboardRegistry()

    @staticmethod
    async def get_buttons(
            keyboard_data,
            dynamic_keyboards_parameters
    ):
        """
        Fetches the button data for a given keyboard.

        :param keyboard_data: Data related to a keyboard.
        :param dynamic_keyboards_parameters: Optional parameters for dynamic keyboards.
        :return: List of button rows.
        """
        if callable(keyboard_data.buttons):
            return keyboard_data.buttons(dynamic_keyboards_parameters)
        return keyboard_data.buttons

    @staticmethod
    async def translate_buttons(
            aiogram_message_manager,
            buttons
    ):
        """
        Translates the text of buttons using a message manager.

        :param aiogram_message_manager: The manager to get translated messages.
        :param buttons: List of button rows.
        :return: List of translated button rows.
        """

        translated_buttons = []

        for button_row in buttons:
            translated_row = []
            for button_tuple in button_row:
                translated_text = aiogram_message_manager.get_message(button_tuple[0])
                translated_row.append((translated_text, *button_tuple[1:]))
            translated_buttons.append(translated_row)

        return translated_buttons

    async def generate_keyboard(
            self,
            aiogram_message_manager,
            key: str,
            dynamic_keyboard_parameters,
            resize_keyboard=True
    ):
        """
        Generates a keyboard based on the provided key and parameters.

        :param aiogram_message_manager: The manager to get translated messages.
        :param key: The key to identify the type of keyboard.
        :param dynamic_keyboard_parameters: Optional parameters for dynamic keyboards.
        :param resize_keyboard: Boolean indicating if the keyboard should be resized.
        :return: An instance of either InlineKeyboardMarkup or ReplyKeyboardMarkup or None if keyboard data isn't found.
        """
        keyboard_data = await self.keyboard_registry.get_keyboard(key)

        if not keyboard_data:
            return None

        creator = keyboard_data.type.value

        buttons = await self.translate_buttons(
            aiogram_message_manager,
            await self.get_buttons(keyboard_data, dynamic_keyboard_parameters)
        )

        return creator.create_keyboard(self, buttons, resize_keyboard)

