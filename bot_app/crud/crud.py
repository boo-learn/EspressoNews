from typing import Optional

from sqlalchemy.orm import Session

from shared.models import Channel, Subscription


def get_subscribed_channels(user_id: int, db: Session):
    subscribed_channels = (
        db.query(Channel)
        .join(Subscription, Channel.channel_id == Subscription.channel_id)
        .filter(Subscription.user_id == user_id, Subscription.is_active is True)
        .all()
    )
    return subscribed_channels


def create_channel(session: Session, channel_username: str, channel_name: str, channel_data) -> Channel:
    channel = Channel(
        channel_name=channel_name,
        channel_username=channel_username,
        description=channel_data.description,
        member_count=channel_data.member_count,
        channel_invite_link=channel_data.invite_link,
    )
    session.add(channel)
    session.commit()
    return channel


def update_subscription(session: Session, user_id: int, channel: Channel) -> Subscription:
    subscription = session.query(Subscription).filter_by(user_id=user_id, channel_id=channel.channel_id).first()
    if not subscription:
        subscription = Subscription(user_id=user_id, channel_id=channel.channel_id)
        session.add(subscription)
    else:
        subscription.is_active = True
    session.commit()
    return subscription


def get_channel(session: Session, channel_username: str) -> Optional[Channel]:
    return session.query(Channel).filter_by(channel_username=channel_username).first()