from shared.rabbitmq import Producer, QueuesType, MessageData
from shared.config import RABBIT_HOST


async def send_to_subscribe_channel(type: str, msg: str):
    message: MessageData = {
        "type": type,
        "data": msg
    }
    producer = Producer(host=RABBIT_HOST, queue=QueuesType.subscription_service)
    await producer.send_message(message, QueuesType.subscription_service)


async def send_to_unsubscribe_channel(type: str, msg: tuple):
    message: MessageData = {
        "type": type,
        "data": msg
    }
    producer = Producer(host=RABBIT_HOST, queue=QueuesType.subscription_service)
    await producer.send_message(message, QueuesType.subscription_service)