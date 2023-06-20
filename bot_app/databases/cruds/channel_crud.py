from bot_app.databases.repositories import ChannelRepository
from shared.config import RABBIT_HOST
from shared.rabbitmq import Producer, QueuesType


class ChannelCRUD:
    def __init__(self):
        self.repository = ChannelRepository()

    def create_channel(self, user_id: int, username: str, name: str, description: str, invite_link: str,
                       members_count: int):
        data = {
            'user_id': user_id,
            'channel_username': username,
            'channel_name': name,
            'member_count': members_count,
            'channel_description': description,
            'channel_invite_link': invite_link,
        }

        return self.repository.create(**data)

    def get_channel(self, channel_username):
        return self.repository.get(channel_username)

    def delete_channel(self, channel):
        return self.repository.delete(channel)

    def check_channel_and_create_if_empty(self, user_id, username: str, name: str, description: str,
                                          invite_link: str, members_count: int):
        channel = self.repository.get(username)

        if not channel:
            channel = self.create_channel(user_id, username, name, description, invite_link, members_count)

        # producer = Producer(host=RABBIT_HOST)
        # await producer.send_message(message='subscribe', queue=QueuesType.subscription_service)
        # await producer.close()

        return channel

    # скорее всего ещё передать user_id
    def check_channel_and_delete_if_empty(self, channel):
        if not channel.subscriptions:
            self.repository.delete(channel)

        # producer = Producer(host=RABBIT_HOST)
        # await producer.send_message(message='unsubscribe', queue=QueuesType.subscription_service)
        # await producer.close()

        return True


