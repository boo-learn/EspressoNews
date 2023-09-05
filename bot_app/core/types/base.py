from abc import ABC, abstractmethod

from shared.rabbitmq import Subscriber


class Router(ABC):
    @abstractmethod
    def register_routes(
            self,
            subscriber: Subscriber
    ):
        pass


class AiogramMessageSender(ABC):
    """
    Abstract base class for message senders.
    """

    @abstractmethod
    async def send(
            self,
            aiogram_message_manager,
            message_key,
            chat_id=None,
            reply_markup=None,
            off_preview=True,
            **message_kwargs
    ):
        """
        Sends a message using the specific message sender implementation.

        :param aiogram_message_manager: The AiogramMessageManager instance.
        :param message_key: The key for the message content.
        :param chat_id: Need for abstract sender.
        :param reply_markup: Optional reply markup for the message.
        :param off_preview: Optional flag to disable web page preview.
        :param message_kwargs: Additional keyword arguments for message content formatting.
        """
        pass


class RabbitMQMessageSender(ABC):
    """
    Abstract base class for RabbitMQ message senders.
    """

    @abstractmethod
    async def send(
            self,
            rmq_message_manager,
            message_content,
            routing_key,
            **kwargs
    ):
        """
        Sends a message using the specific RabbitMQ message sender implementation.

        :param rmq_message_manager: The RabbitMQMessageManager instance.
        :param message_content: The content of the message to be sent.
        :param routing_key:
        :param kwargs: Additional keyword arguments for sending configurations.
        """
        pass


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