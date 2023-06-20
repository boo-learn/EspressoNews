from bot_app.databases.cruds import ChannelCRUD
from bot_app.databases.repositories import SubscriptionRepository
from shared.config import RABBIT_HOST
from shared.rabbitmq import Producer, QueuesType


class SubscriptionCRUD:
    def __init__(self):
        self.repository = SubscriptionRepository()

    def get_subscription(self, user_id, channel):
        return self.repository.get(user_id, channel)

    def update_subscription(self, user_id, channel, switch=True):
        subscription = self.repository.get(user_id, channel)

        if switch == True:
            if not subscription:
                self.repository.create(user_id, channel)
            else:
                self.repository.update_status(subscription)
        else:
            self.repository.delete(subscription)

        return subscription

    def get_subscribed_channels(self, user_id):
        return self.repository.get_channels(user_id)

    def delete_subscription(self, subscription):
        return self.repository.delete(subscription)

    def check_channel_and_delete_if_empty(self, channel):
        remaining_subscriptions = self.repository.get_channels_count(channel)

        if remaining_subscriptions == 0:
            channel_crud = ChannelCRUD()
            channel_crud.delete_channel(channel)

            # Шлем сообщение в редис
            # producer = Producer(host=RABBIT_HOST)
            # await producer.send_message(message='unsubscribe', queue=QueuesType.subscription_service)
            # await producer.close()

        return True
