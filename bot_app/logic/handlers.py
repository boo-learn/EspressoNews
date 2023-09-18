from shared.config import RABBIT_HOST
from shared.rabbitmq import Subscriber, QueuesType
from bot_app.loader import bot
import json


async def send_message_to_users(message: str):
    data = json.loads(message)
    # Message format:
    # total_message = {
    #     "message_text": message,
    #     "user_ids": user_ids
    # }
    for user_id in data["user_ids"]:
        await bot.send_message(user_id, data["message_text"])


async def subscribe_on_rabbit_messages():
    subscriber = Subscriber(host=RABBIT_HOST, queue=QueuesType.bot_service)
    subscriber.subscribe("send_message", send_message_to_users)
    await subscriber.run()
