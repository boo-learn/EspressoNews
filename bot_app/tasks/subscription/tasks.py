from shared.rabbitmq import Producer, QueuesType, MessageData
from shared.config import RABBIT_HOST


async def send_to_subscribe_channel(type: str):
    message: MessageData = {
        "type": type,
        "data": None
    }
    producer = Producer(host=RABBIT_HOST, queue=QueuesType.subscription_service)
    await producer.send_message(message, QueuesType.subscription_service)
