from bot_app.databases.cruds import ChannelCRUD
from bot_app.databases.repositories import SubscriptionRepository
from bot_app.tasks.subscription.tasks import send_to_subscribe_channel, send_to_unsubscribe_channel
from shared.config import RABBIT_HOST
from shared.rabbitmq import Producer, QueuesType


class SubscriptionCRUD:
    def __init__(self):
        self.repository = SubscriptionRepository()

    async def get_subscription(self, user_id, channel):
        return await self.repository.get(user_id, channel.channel_id)

    async def update_subscription(self, user_id, channel, switch=True):
        subscription = await self.repository.get(user_id, channel.channel_id)

        if switch:
            if not subscription:
                await self.repository.create(user_id, channel)
            else:
                await self.repository.update_status(subscription)
        else:
            await self.repository.delete(subscription)

        return subscription

    async def get_subscribed_channels(self, user_id):
        return await self.repository.get_channels(user_id)

    async def delete_subscription(self, subscription):
        return await self.repository.delete(subscription)

    async def check_channel_and_delete_if_empty(self, channel):
        remaining_subscriptions = await self.repository.get_channels_count(channel.channel_id)

        if remaining_subscriptions == 0:
            channel_crud = ChannelCRUD()
            await channel_crud.delete_channel(channel)

            await send_to_unsubscribe_channel("unsubscribe", (channel.channel_username, channel.account_id))

        return True
