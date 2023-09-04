from shared.rabbitmq import Producer, QueuesType, MessageData
from shared.config import RABBIT_HOST


class ChannelRouter:
    def __init__(self):
        self.producer = Producer(host=RABBIT_HOST, queue=QueuesType.subscription_service)

    async def send_to_subscribe(
            self,
            type: str,
            msg: str
    ):
        message: MessageData = {
            "type": type,
            "data": msg
        }
        await self.producer.send_message(message, QueuesType.subscription_service)

    async def send_to_unsubscribe(
            self,
            type: str,
            msg: str,
            account_id: int
    ):
        message: MessageData = {
            "type": type,
            "data": (msg, account_id)
        }
        await self.producer.send_message(message, QueuesType.subscription_service)
