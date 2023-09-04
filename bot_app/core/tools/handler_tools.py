from bot_app.core.handlers.registrar import HandlerRegistrar
from bot_app.core.messages.senders import AnswerSender
from bot_app.core.messages.manager import MessageManager
from bot_app.core.metaclases.singleton import SingletonMeta


class HandlersTools(metaclass=SingletonMeta):
    """
    Singleton class providing essential tools for message handlers.

    Attributes:
        registrar (HandlerRegistrar): An instance for registering and managing message handlers.
        message_manager (MessageManager): Manages the process of obtaining and sending messages.
        _ (function): Lambda function as a shorthand for getting translated messages.

    Note:
        HandlersTools is a singleton, ensuring that only one instance of the class is created.
        It centralizes the management of message handling tools, making it easier for handlers
        to access and use common tools without creating multiple instances.
    """

    def __init__(self):
        """
        Initializes the HandlersTools instance with essential components like registrar and message manager.
        """
        self.registrar = HandlerRegistrar()
        self.message_manager = MessageManager(sender=AnswerSender())
        self._ = lambda key: self.message_manager.get_message(key)

    def update_message(self, message) -> None:
        """
        Update the current message in the message manager.

        :param message: The message to be set in the message manager.
        """
        self.message_manager.set_message(message)

    def update_language(self, lang_code) -> None:
        """
        Update the current message in the message manager.

        :param lang_code: Lang code for translates.
        """
        self.message_manager.set_language(lang_code)
