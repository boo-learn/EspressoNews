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
            message_manager,
            buttons
    ):
        """
        Translates the text of buttons using a message manager.

        :param message_manager: The manager to get translated messages.
        :param buttons: List of button rows.
        :return: List of translated button rows.
        """

        translated_buttons = []

        for button_row in buttons:
            translated_row = []
            for button_tuple in button_row:
                translated_text = message_manager.get_message(button_tuple[0])
                logger.info(
                    f'21 шаг - смотрим как переводит кнопки \n \n'
                    f'{button_tuple[0]} \n \n'
                    f'{translated_text} \n \n'
                )
                translated_row.append((translated_text, *button_tuple[1:]))
            translated_buttons.append(translated_row)

        return translated_buttons

    async def generate_keyboard(
            self,
            message_manager,
            key: str,
            dynamic_keyboard_parameters,
            resize_keyboard=True
    ):
        """
        Generates a keyboard based on the provided key and parameters.

        :param message_manager: The manager to get translated messages.
        :param key: The key to identify the type of keyboard.
        :param dynamic_keyboard_parameters: Optional parameters for dynamic keyboards.
        :param resize_keyboard: Boolean indicating if the keyboard should be resized.
        :return: An instance of either InlineKeyboardMarkup or ReplyKeyboardMarkup or None if keyboard data isn't found.
        """
        keyboard_data = await self.keyboard_registry.get_keyboard(key)

        if not keyboard_data:
            return None

        logger.info(
            f'Восемнадцатый шаг - получили данные клавиатуры по коду \n \n'
            f'{keyboard_data} \n \n'
            f'{keyboard_data.type} \n \n'
            f'{keyboard_data.buttons} \n \n'
        )

        creator = keyboard_data.type.value

        logger.info(
            f'19 шаг - Установлен объект создателя \n \n'
            f'{creator} \n \n'
        )

        logger.info(
            f'20 шаг - получаем кнопки без перевода \n \n'
            f'{await self.get_buttons(keyboard_data, dynamic_keyboard_parameters)} \n \n'
        )

        buttons = await self.translate_buttons(
            message_manager,
            await self.get_buttons(keyboard_data, dynamic_keyboard_parameters)
        )

        logger.info(
            f'22 шаг - кнопки переведены \n \n'
            f'{buttons} \n \n'
        )

        return creator.create_keyboard(self, buttons, resize_keyboard)

