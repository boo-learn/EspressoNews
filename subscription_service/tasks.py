from telethon.tl.functions.channels import JoinChannelRequest, LeaveChannelRequest
from telethon.tl.types import InputChannel

from shared.celery_app import celery_app
from shared.database import SessionLocal
from shared.models import Subscription, Channel, TelegramAccount
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import GetChannelsRequest


@celery_app.task
def subscribe(user_id, channel_id):
    session = SessionLocal()
    account = session.query(TelegramAccount).filter(TelegramAccount.is_active is True).first()

    if account:
        with TelegramClient(account.phone_number, account.api_id, account.api_hash) as client:
            channel = session.query(Channel).get(channel_id)
            if channel:
                # Получаем текущие подписки бота
                current_subscriptions = client(GetChannelsRequest([InputChannel(channel_id, 0)]))
                current_channel_usernames = [c.username for c in current_subscriptions.chats]

                # Если бот еще не подписан на канал, подписываемся
                if channel.channel_username not in current_channel_usernames:
                    client(JoinChannelRequest(channel.channel_invite_link))

                subscription = Subscription(user_id=user_id, channel_id=channel_id)
                session.add(subscription)
                session.commit()


@celery_app.task
def unsubscribe(user_id, channel_id):
    session = SessionLocal()
    account = session.query(TelegramAccount).filter(TelegramAccount.is_active is True).first()

    if account:
        with TelegramClient(account.phone_number, account.api_id, account.api_hash) as client:
            channel = session.query(Channel).get(channel_id)
            if channel:
                subscription = session.query(Subscription).filter(Subscription.user_id == user_id,
                                                                  Subscription.channel_id == channel_id).first()
                if subscription:
                    session.delete(subscription)
                    session.commit()

                # Если больше нет подписчиков на канал, отписываем бота
                remaining_subscriptions = session.query(Subscription).filter(
                    Subscription.channel_id == channel_id).count()
                if remaining_subscriptions == 0:
                    client(LeaveChannelRequest(channel.channel_username))
