import asyncio
import logging

from bot_app.databases.repositories import ChannelRepository
from bot_app.tasks.subscription.tasks import send_to_subscribe_channel

logger = logging.getLogger(__name__)


class ChannelCRUD:
    def __init__(self):
        self.repository = ChannelRepository()

    async def create_channel(self, id: int, username: str, name: str, description: str, invite_link: str,
                             members_count: int):
        data = {
            'channel_id': id,
            'channel_username': username,
            'channel_name': name,
            'member_count': members_count,
            'channel_description': description,
            'channel_invite_link': invite_link,
        }

        return await self.repository.create(**data)

    async def get_channel(self, channel_username):
        return await self.repository.get(channel_username)

    async def delete_channel(self, channel):
        return await self.repository.delete(channel)

    async def check_channel_and_create_if_empty(self, id: int, username: str, name: str, description: str,
                                                invite_link: str, members_count: int):
        channel = await self.repository.get(username)

        if not channel:
            channel = await self.create_channel(id, username, name, description, invite_link, members_count)
            channel = await self.repository.get(username)

        # send_message_subscribe
        await send_to_subscribe_channel("subscribe")

        return channel

    # скорее всего ещё передать user_id
    async def check_channel_and_delete_if_empty(self, channel):
        logger.debug(f"Checking if channel {channel} is empty")

        logger.debug(f"CHANNEL SUBSCRIPTIONS {channel.subscriptions}")
        if not channel.subscriptions:
            logger.debug(f"Channel {channel} is empty, deleting")
            await self.repository.delete(channel)
            await send_to_subscribe_channel("unsubscribe")
        else:
            logger.debug(f"Channel {channel} has subscriptions, not deleting")

        logger.debug("Sending unsubscribe message to subscribe channel")

        logger.debug("Successfully completed check_channel_and_delete_if_empty")

        return True
