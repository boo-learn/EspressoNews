from bot_app.databases.repositories import ChannelRepository
from shared.config import RABBIT_HOST
from shared.rabbitmq import Producer, QueuesType


class ChannelCRUD:
    def __init__(self):
        self.repository = ChannelRepository()

    async def create_channel(self, username: str, name: str, description: str, invite_link: str,
                             members_count: int):
        data = {
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

    async def check_channel_and_create_if_empty(self, username: str, name: str, description: str,
                                                invite_link: str, members_count: int):
        channel = await self.repository.get(username)

        if not channel:
            channel = await self.create_channel(username, name, description, invite_link, members_count)
            channel = await self.repository.get(username)

        # producer = Producer(host=RABBIT_HOST)
        # await producer.send_message(message='subscribe', queue=QueuesType.subscription_service)
        # await producer.close()

        return channel

    # скорее всего ещё передать user_id
    async def check_channel_and_delete_if_empty(self, channel):
        if not channel.subscriptions:
            await self.repository.delete(channel)

        # producer = Producer(host=RABBIT_HOST)
        # await producer.send_message(message='unsubscribe', queue=QueuesType.subscription_service)
        # await producer.close()

        return True
