import logging
from abc import ABC, abstractmethod

from bot_app.core.users.crud import UserCRUD
from shared.rabbitmq import Subscriber
from shared.db_utils import update_or_create_schedule_in_db


logger = logging.getLogger(__name__)


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


class MailingManager(ABC):
    def __init__(self):
        self.user_crud = UserCRUD()

    async def _base_create_rule_for_all(
            self,
            task_name_template: str,
            task_func: str,
            cron_periodicity: str = None,
            setting_option: str = None
    ):
        logger.info(f"Starting to create rules for {task_name_template}...")

        if cron_periodicity:
            user_ids = await self.user_crud.get_all_user_ids()
            users_list_periodicity_options = [cron_periodicity for _ in user_ids]
        else:
            user_ids, users_list_periodicity_options = await self.user_crud.get_settings_option_for_all_users(
                setting_option
            )

        for user_id, option in zip(user_ids, users_list_periodicity_options):
            await self.create_rule(user_id, option, task_name_template, task_func)

        logger.info(f"Finished creating rules for {task_name_template}.")

    @staticmethod
    async def _base_create_rule(
            user_id: int,
            cron_periodicity: str,
            task_name_template: str,
            task_func: str
    ):
        logger.info(f"Starting to create rule for user {user_id} with task {task_name_template}...")
        logger.info(f"Got settings option for user {user_id}.")
        task_name = f"{task_name_template}-for-{str(user_id)}"
        task_schedule = {
            'task': task_func,
            'schedule': cron_periodicity,
            'args': (user_id,),
        }

        logging.info(f"{task_schedule}")
        await update_or_create_schedule_in_db(task_name, task_schedule)

        logger.info(f"Finished creating rule for user {user_id} with task {task_name_template}.")

    @abstractmethod
    async def create_rule_for_all(
            self,
            task_name_template: str,
            task_func: str,
            cron_periodicity: str = None,
            setting_option: str = None
    ):
        pass

    @abstractmethod
    async def create_rule(
            self,
            user_id: int,
            cron_periodicity: str,
            task_name_template: str,
            task_func: str
    ):
        pass
