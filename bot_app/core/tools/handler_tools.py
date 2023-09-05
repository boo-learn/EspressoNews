from bot_app.core.routers.registrars import AiogramRoutesRegistrar, RabbitMQRoutesRegistrar
from bot_app.core.messages.senders import AnswerSender
from bot_app.core.messages.manager import AiogramMessageManager, RabbitMQMessageManager
from bot_app.core.metaclases.singleton import SingletonMeta


class HandlersTools(metaclass=SingletonMeta):
    """
    Singleton class providing essential tools for message routers.

    Attributes:
        aiogram_registrar (AiogramRoutesRegistrar): An instance for registering and managing message routers.
        rmq_registrar (RabbitMQRoutesRegistrar): An instance for registering and managing message routers.
        aiogram_message_manager (AiogramMessageManager): Manages the process of obtaining and sending messages.
        rmq_message_manager (RabbitMQMessageManager): Manages the process sending messages.
        _ (function): Lambda function as a shorthand for getting translated messages.

    Note:
        HandlersTools is a singleton, ensuring that only one instance of the class is created.
        It centralizes the management of message handling tools, making it easier for routers
        to access and use common tools without creating multiple instances.
    """

    def __init__(self):
        """
        Initializes the HandlersTools instance with essential components like registrar and message manager.
        """
        self.aiogram_registrar = AiogramRoutesRegistrar()
        self.rmq_registrar = RabbitMQRoutesRegistrar()
        self.aiogram_message_manager = AiogramMessageManager(sender=AnswerSender())
        self.rmq_message_manager = RabbitMQMessageManager()
        self._ = lambda key: self.aiogram_message_manager.get_message(key)

    def update_message(self, message) -> None:
        """
        Update the current message in the message manager.

        :param message: The message to be set in the message manager.
        """
        self.aiogram_message_manager.set_message(message)

    def update_language(self, lang_code) -> None:
        """
        Update the current message in the message manager.

        :param lang_code: Lang code for translates.
        """
        self.aiogram_message_manager.set_language(lang_code)

    def update_queue(self, queue_name):
        """
        Update the queue_name in the message manager.

        :param queue_name: Queue name for sending.
        """
        self.rmq_message_manager.set_queue_name(queue_name)
