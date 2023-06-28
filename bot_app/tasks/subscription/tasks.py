from shared.rabbitmq import Producer, QueuesType, MessageData
from shared.config import RABBIT_HOST


async def subscribe_to_channel():
    message: MessageData = {
        "type": "subscribe",
        "data": None
    }
    producer = Producer(host=RABBIT_HOST)
    await producer.send_message(message, QueuesType.subscription_service)