from __future__ import annotations

from enum import Enum
from abc import ABC, abstractmethod
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from typing import List, Tuple


class KeyboardCreator(ABC):
    """
    Abstract base class for keyboard creators. Defines the interface for creating keyboards.
    """

    @abstractmethod
    def create_keyboard(
            self,
            keyboard_manager,
            buttons,
            resize_keyboard
    ):
        """
        Abstract method to create a keyboard.

        :param keyboard_manager: The keyboard manager instance.
        :param buttons: A list of button rows, where each row is a list of button tuples.
        :param resize_keyboard: Boolean indicating if the keyboard should be resized.
        :return: An instance of either InlineKeyboardMarkup or ReplyKeyboardMarkup.
        """
        pass


class InlineKeyboardCreator(KeyboardCreator):
    """
    Concrete creator for inline keyboards.
    """
    def create_keyboard(
            self,
            keyboard_manager,
            buttons: List[List[Tuple[str, str, str | None]]],
            resize_keyboard: bool = True
    ) -> InlineKeyboardMarkup:
        """
        Creates an inline keyboard.

        :param keyboard_manager: The keyboard manager instance.
        :param buttons: A list of button rows, where each row is a list of button tuples (text, callback_data, url).
        :param resize_keyboard: Boolean indicating if the keyboard should be resized.
        :return: An instance of InlineKeyboardMarkup.
        """
        keyboard = InlineKeyboardMarkup(resize_keyboard=resize_keyboard)

        for row in buttons:
            row_buttons = [
                InlineKeyboardButton(
                    text=text,
                    callback_data=callback_data,
                    url=url
                ) for text, callback_data, url in row
            ]
            keyboard.row(*row_buttons)
        return keyboard


class ReplyKeyboardCreator(KeyboardCreator):
    """
    Concrete creator for reply keyboards.
    """
    def create_keyboard(
            self,
            keyboard_manager,
            buttons: List[List[Tuple[str]]],
            resize_keyboard: bool = True
    ) -> ReplyKeyboardMarkup:
        """
        Creates a reply keyboard.

        :param keyboard_manager: The keyboard manager instance.
        :param buttons: A list of button rows, where each row is a list of button tuples.
        :param resize_keyboard: Boolean indicating if the keyboard should be resized.
        :return: An instance of ReplyKeyboardMarkup.
        """
        keyboard = ReplyKeyboardMarkup(resize_keyboard=resize_keyboard)

        for row in buttons:
            row_buttons = [KeyboardButton(text=button[0]) for button in row]
            keyboard.row(*row_buttons)
        return keyboard


class KeyboardType(Enum):
    """
    Enum to represent different types of keyboards. Maps each type to its respective creator.
    """
    REPLY = ReplyKeyboardCreator()
    INLINE = InlineKeyboardCreator()
