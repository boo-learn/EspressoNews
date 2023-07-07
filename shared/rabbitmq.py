import asyncio
import json
import aio_pika
import enum
from collections.abc import Callable
from typing import TypedDict, Any, Union, Callable


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
    def __init__(self, host="localhost"):
        self.host_url = f"amqp://guest:guest@{host}/"
        self.connection = None
        self.channel = None

    async def __connect(self):
        if self.connection:
            return
        print("Producer new connection")
        self.connection = await aio_pika.connect_robust(self.host_url)
        self.channel = await self.connection.channel()

    async def send_message(self, message_with_data: MessageData, queue: QueuesType, answer_callback=None):
        if not self.connection or self.connection.is_closed:
            await self.__connect()
        await self.channel.declare_queue(queue.value)

        message = aio_pika.Message(body=json.dumps(message_with_data, ensure_ascii=False).encode())
        await self.channel.default_exchange.publish(message, routing_key=queue.value)

        print(f"Message sent: {message.body.decode()}")

    # TODO: переписать деструктор на асинхронную работу
    def __del__(self):
        if self.connection:
            self.connection.close()


class Subscriber(metaclass=SingletonMeta):
    # __metaclass__ = Singleton

    def __init__(self, host: str, queue: QueuesType):
        self.host_url = f"amqp://guest:guest@{host}/"
        self.queue_name: str = queue.value
        self.connection = None
        self.channel = None
        self.queue = None
        self.handlers: dict[str, Callable] = {}

    async def __on_message(self, message: aio_pika.IncomingMessage):
        # print(f"Raw message = {message.body.decode()}")
        message_body = json.loads(message.body.decode())
        async with message.process():
            if message_body["data"]:
                await self.handlers[message_body["type"]](message_body["data"])
            else:
                await self.handlers[message_body["type"]]()
            # print(f"[x] Received message: {message.body.decode()}")

    async def __connect(self, retries=10, delay=5):
        if self.connection:
            return
        for i in range(retries):
            try:
                self.connection = await aio_pika.connect_robust(self.host_url)
                self.channel = await self.connection.channel()
                await self.channel.set_qos(prefetch_count=1)
                self.queue = await self.channel.declare_queue(self.queue_name)
            except Exception as e:
                if i < retries - 1:
                    print(f"Failed to connect to RabbitMQ: {e}. Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                    continue
                else:
                    print("Failed to connect to RabbitMQ after several attempts. Exiting...")
                    raise

    async def __start_subscribe(self):
        if not self.connection or self.connection.is_closed:
            await self.__connect()
        await self.queue.consume(self.__on_message)

    def subscribe(self, message_type: str, callback: Callable):
        self.handlers[message_type] = callback

    async def run(self):
        await self.__connect()
        await self.__start_subscribe()

    # TODO: переписать деструктор на асинхронную работу
    def __del__(self):
        if self.connection:
            self.connection.close()
