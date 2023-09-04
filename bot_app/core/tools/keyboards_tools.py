from __future__ import annotations

from typing import List, Tuple, Callable

from bot_app.core.keyboards.creators import KeyboardType
from bot_app.core.keyboards.registrar import KeyboardRegistry
from bot_app.core.metaclases.singleton import SingletonMeta


class KeyboardsTools(metaclass=SingletonMeta):
    """
    Singleton class that provides essential tools for keyboard management.

    Attributes:
        registrar (KeyboardRegistry): An instance for registering and managing keyboards.

    Note:
        KeyboardsTools is a singleton, ensuring that only one instance of the class is created.
        It centralizes the management of keyboard tools, making it easier to access and use
        common keyboard-related functionalities without creating multiple instances.
    """

    def __init__(self):
        """
        Initializes the KeyboardsTools instance by setting up the keyboard registrar.
        """
        self.registrar = KeyboardRegistry()

    def register(
            self,
            key: str,
            keyboard_type: KeyboardType,
            buttons: List[List[Tuple[str | None, ...]]] | Callable
    ) -> None:
        """
        Register a new keyboard with the provided key, type, and buttons.

        :param key: The unique identifier for the keyboard.
        :param keyboard_type: The type of the keyboard (e.g., INLINE, REPLY).
        :param buttons: The buttons for the keyboard, can either be a list of tuples or a callable.
        """
        self.registrar.register_keyboard(key, keyboard_type, buttons)
