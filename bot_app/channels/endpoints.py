from bot_app.core.tools.handler_tools import HandlersTools
from shared.rabbitmq import MessageData


class ChannelHandlers(HandlersTools):
    async def send_to_subscribe(self, type: str, msg: str):
        message: MessageData = {
            "type": type,
            "data": msg
        }
        self.update_queue('subscription_service')
        await self.rmq_message_manager.send_message(message, 'subscription_service')

    async def send_to_unsubscribe(self, type: str, msg: str, account_id: int):
        message: MessageData = {
            "type": type,
            "data": (msg, account_id)
        }
        self.update_queue('subscription_service')
        await self.rmq_message_manager.send_message(message, 'subscription_service')
