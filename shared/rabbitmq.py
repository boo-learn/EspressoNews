import asyncio
import aio_pika
import enum
from collections.abc import Callable


class QueuesType(enum.Enum):
    news_collection_service = "news"
    subscription_service = "subscription"
    bot_service = "bot"


# class MessageTypes(enum.Enum):

class Producer:
    def __init__(self, host="localhost"):
        self.host_url = f"amqp://guest:guest@{host}/"
        self.connection = None
        self.channel = None

    async def __connect(self):
        self.connection = await aio_pika.connect_robust(self.host_url)
        self.channel = await self.connection.channel()

    async def send_message(self, message: str, queue: QueuesType):
        if not self.connection or self.connection.is_closed:
            await self.__connect()
        await self.channel.declare_queue(queue.value)

        message = aio_pika.Message(body=message.encode())
        await self.channel.default_exchange.publish(message, routing_key=queue.value)

        print(f"Message sent: {message.body.decode()}")

    async def close(self):
        if self.connection:
            await self.connection.close()


class Subscriber:
    def __init__(self, host: str, queue: QueuesType):
        self.host_url = f"amqp://guest:guest@{host}/"
        self.queue_name: str = queue.value
        self.connection = None
        self.channel = None
        self.queue = None
        self.handlers: dict[str, Callable] = {}

    async def __on_message(self, message: aio_pika.IncomingMessage):
        async with message.process():
            self.handlers[message.body.decode()]()
            # print(f"[x] Received message: {message.body.decode()}")

    async def __connect(self):
        self.connection = await aio_pika.connect_robust(self.host_url)
        self.channel = await self.connection.channel()
        await self.channel.set_qos(prefetch_count=1)
        self.queue = await self.channel.declare_queue(self.queue_name)

    async def __start_subscribe(self):
        # print(f"Started listening to '{self.queue_name}'")
        if not self.connection or self.connection.is_closed:
            await self.__connect()
        await self.queue.consume(self.__on_message)

    def subscribe(self, message: str, callback: Callable):
        self.handlers[message] = callback

    async def run(self):
        await self.__connect()
        await self.__start_subscribe()
