import logging
from typing import List

from bot_app.channels.endpoints import ChannelHandlers
from bot_app.databases.repositories import ChannelRepository
from bot_app.databases.repositories import SubscriptionRepository
from shared.models import Channel

logger = logging.getLogger(__name__)


class ChannelCRUD:
    def __init__(self):
        self.repository = ChannelRepository()

    async def create_channel(
            self,
            id: int,
            username: str,
            name: str,
            description: str,
            invite_link: str,
            members_count: int
    ):
        data = {
            'channel_id': id,
            'channel_username': username,
            'channel_name': name,
            'member_count': members_count,
            'channel_description': description,
            'channel_invite_link': invite_link,
        }

        return await self.repository.create(**data)

    async def get_channel(
            self,
            channel_username
    ):
        return await self.repository.get(channel_username)

    async def get_channel_by_id(
            self,
            channel_id
    ):
        return await self.repository.get_by_id(channel_id)

    async def delete_channel(
            self,
            channel
    ):
        return await self.repository.delete(channel)

    async def check_channel_and_create_if_empty(
            self,
            id: int,
            username: str,
            name: str,
            description: str,
            invite_link: str,
            members_count: int
    ):
        channel = await self.repository.get(username)

        if not channel:
            await self.create_channel(id, username, name, description, invite_link, members_count)
            channel = await self.repository.get(username)

        # send_message_subscribe
        channel_handlers = ChannelHandlers()
        await channel_handlers.send_to_subscribe("subscribe", username)
        return channel

    # скорее всего ещё передать user_id
    async def check_channel_and_delete_if_empty(self, channel):
        logger.debug(f"Checking if channel {channel} is empty")

        logger.debug(f"CHANNEL SUBSCRIPTIONS {channel.subscriptions}")
        if not channel.subscriptions:
            logger.debug(f"Channel {channel} is empty, deleting")
            await self.repository.delete(channel)

            channel_handlers = ChannelHandlers()
            await channel_handlers.send_to_unsubscribe(
                "unsubscribe",
                channel.channel_username,
                channel.account_id
            )
        else:
            logger.debug(f"Channel {channel} has subscriptions, not deleting")

        logger.debug("Sending unsubscribe message to subscribe channel")

        logger.debug("Successfully completed check_channel_and_delete_if_empty")

        return True


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

    async def get_subscribed_channels(self, user_id) -> List[Channel]:
        return await self.repository.get_channels(user_id)

    async def delete_subscription(self, subscription):
        return await self.repository.delete(subscription)

    async def check_channel_and_delete_if_empty(self, channel):
        remaining_subscriptions = await self.repository.get_channels_count(channel.channel_id)

        if remaining_subscriptions == 0:
            channel_crud = ChannelCRUD()
            await channel_crud.delete_channel(channel)

            channel_handlers = ChannelHandlers()
            await channel_handlers.send_to_unsubscribe(
                "unsubscribe",
                channel.channel_username,
                channel.account_id
            )

        return True
