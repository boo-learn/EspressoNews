from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import List, Tuple, Callable, Optional, Union

from bot_app.core.keyboards.creators import KeyboardType
from bot_app.core.metaclases.singleton import SingletonMeta


logger = logging.getLogger(__name__)


@dataclass
class KeyboardData:
    """
    Data representation of a keyboard, including its type and buttons.

    Attributes:
        type (KeyboardType): The type of the keyboard (e.g., INLINE or REPLY).
        buttons (Union[List[List[Tuple[str | None, ...]]], Callable]): The buttons for the keyboard or a callable
            to generate the buttons dynamically.
    """
    type: KeyboardType
    buttons: Union[List[List[Tuple[str | None, ...]]], Callable]


class KeyboardRegistry(metaclass=SingletonMeta):
    """
    A registry for storing and retrieving keyboard data.

    Attributes:
        keyboards (dict): A dictionary that maps a key to its respective keyboard data.
    """

    def __init__(self) -> None:
        """
        Initializes a new instance of the KeyboardRegistry.
        """
        self.keyboards = {}

    async def get_keyboard(self, key: str) -> Optional[KeyboardData]:
        """
        Retrieves the keyboard data associated with the given key.

        :param key: The key to identify the keyboard data.
        :return: The keyboard data if found; otherwise, None.
        """
        return self.keyboards.get(key, None)

    def register_keyboard(
            self,
            key: str,
            keyboard_type: KeyboardType,
            buttons: Union[List[List[Tuple[str | None, ...]]], Callable]
    ) -> None:
        """
        Registers keyboard data to the registry.

        :param key: The key to identify the keyboard data.
        :param keyboard_type: The type of the keyboard (e.g., INLINE or REPLY).
        :param buttons: The buttons for the keyboard or a callable to generate the buttons dynamically.
        """
        self.keyboards[key] = KeyboardData(type=keyboard_type, buttons=buttons)
