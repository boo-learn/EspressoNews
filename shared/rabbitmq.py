import asyncio
import json
import logging
import traceback
import aio_pika
import enum
from collections.abc import Callable
from typing import TypedDict, Any, Union, Callable
from shared.loggers import get_logger

MAX_RETRIES = 10
RETRY_DELAY = 5


logger = get_logger('shared.rabbit')


class SingletonMeta(type):
    """
    The Singleton class can be implemented in different ways in Python. Some
    possible methods include: base class, decorator, metaclass. We will use the
    metaclass because it is best suited for this purpose.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class QueuesType(enum.Enum):
    news_collection_service = "news"
    subscription_service = "subscription"
    bot_service = "bot"
    summary_service = "summary"
    digest_service = "digest"
    # Test queues:
    ping = "ping"
    pong = "pong"


class MessageData(TypedDict):
    type: str
    data: Any


class Producer(metaclass=SingletonMeta):
    def __init__(self, host: str, queue: QueuesType):
        logger.info("Initializing Producer")
        self.host_url = f"amqp://guest:guest@{host}/"
        self.queue_name: str = queue.value
        self.connection = None
        self.channel = None
        logger.info("Producer initialized")

    async def __connect(self):
        logger.info("Connecting to the server")
        if self.connection and not self.connection.is_closed and self.channel and not self.channel.is_closed:
            return
        logger.info("Producer new connection")
        self.connection = await aio_pika.connect_robust(self.host_url)
        self.channel = await self.connection.channel()
        await self.channel.declare_queue(self.queue_name)
        logger.info("Connected to the server")

    async def send_message(self, message_with_data: MessageData, queue: QueuesType, answer_callback=None):
        for _ in range(MAX_RETRIES):
            try:
                logger.info("Sending message", connection=str(self.connection))
                connection_is_closed = None if self.connection is None else self.connection.is_closed
                channel_is_closed = None if self.channel is None else self.channel.is_closed

                logger.info(
                    f"Connection {self.connection} is closed {connection_is_closed} self channel {self.channel} is closed {channel_is_closed}")

                if not self.connection or self.connection.is_closed or not self.channel or self.channel.is_closed:
                    logger.info("Try connect")
                    await self.__connect()
                logger.info("Connection is open")
                message = aio_pika.Message(body=json.dumps(message_with_data, ensure_ascii=False).encode())
                await self.channel.default_exchange.publish(message, routing_key=queue.value)

                logger.info(f"Message sent", message=message.body.decode())
                return
            except Exception as e:
                logger.exception(f"Failed to send message", error=e)
                await asyncio.sleep(RETRY_DELAY)
        logger.error(f"Failed to send message after {MAX_RETRIES} attempts")

    def __del__(self):
        logger.info("Closing connection")
        if self.connection and not self.connection.is_closed:
            try:
                asyncio.run(self.connection.close())
            except Exception as e:
                logger.exception('Error closing connection', error=e)
        logger.info('Connection closed')


class Subscriber(metaclass=SingletonMeta):
    # __metaclass__ = Singleton

    def __init__(self, host: str, queue: QueuesType):
        self.host_url = f"amqp://guest:guest@{host}/"
        self.queue_name: str = queue.value
        self.connection = None
        self.channel = None
        self.queue = None
        self.__delay_message_time = 1
        self.handlers: dict[str, Callable] = {}

    async def __on_message(self, message: aio_pika.IncomingMessage):
        logger.info('Got new message')
        self.__delay_message_time += 1
        message_body = json.loads(message.body.decode())
        async with message.process():
            if message_body["data"]:
                await self.handlers[message_body["type"]](message_body["data"])
            else:
                await self.handlers[message_body["type"]]()

    # async def __connect(self, retries=10, delay=5):
    #     if self.connection:
    #         return
    #     for i in range(retries):
    #         try:
    #             self.connection = await aio_pika.connect_robust(self.host_url)
    #             self.channel = await self.connection.channel()
    #             await self.channel.set_qos(prefetch_count=1)
    #             self.queue = await self.channel.declare_queue(self.queue_name)
    #         except Exception as e:
    #             if i < retries - 1:
    #                 print(f"Failed to connect to RabbitMQ: {e}. Retrying in {delay} seconds...")
    #                 await asyncio.sleep(delay)
    #                 continue
    #             else:
    #                 print("Failed to connect to RabbitMQ after several attempts. Exiting...")
    #                 raise

    async def __connect(self):
        if self.connection:
            return
        logger.info('Subscriber new connection')
        self.connection = await aio_pika.connect_robust(self.host_url)
        self.channel = await self.connection.channel()
        await self.channel.set_qos(prefetch_count=1)
        self.queue = await self.channel.declare_queue(self.queue_name)

    async def __start_subscribe(self):
        if not self.connection or self.connection.is_closed:
            await self.__connect()
        await self.queue.consume(self.__on_message)

    def subscribe(self, message_type: str, callback: Callable):
        self.handlers[message_type] = callback

    async def run(self):
        await self.__connect()
        await self.__start_subscribe()

    async def get_all_messages(self):
        """
        method for pytest
        """
        await self.__connect()
        await self.queue.consume(self.__on_message)
        while self.__delay_message_time > 0:
            await asyncio.sleep(0.5)
            self.__delay_message_time -= 0.5
            logger.info('Update delay time', time=self.__delay_message_time)
        await self.connection.close()

    # TODO: переписать деструктор на асинхронную работу
    def __del__(self):
        if self.connection:
            self.connection.close()
