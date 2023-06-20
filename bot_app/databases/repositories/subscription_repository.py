from shared.database import SessionLocal
from shared.models import Subscription, Channel
from sqlalchemy.exc import SQLAlchemyError


class SubscriptionRepository:
    def __init__(self):
        self.session = SessionLocal()

    def create(self, user_id: int, channel: Channel) -> Subscription:
        try:
            subscription = Subscription(user_id=user_id, channel_id=channel.channel_id)
            self.session.add(subscription)
            self.session.commit()
            return subscription
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e

    def get(self, user_id: int, channel: Channel):
        try:
            return self.session.query(Subscription).filter_by(
                user_id=user_id,
                channel_id=channel.channel_id
            ).one_or_none()
        except SQLAlchemyError as e:
            raise e

    def get_channels_count(self, channel: Channel):
        return self.session.query(Subscription).filter(Subscription.channel_id == channel.channel_id).count()

    def get_channels(self, user_id: int):
        try:
            return (
                self.session.query(Channel)
                .join(Subscription, Channel.channel_id == Subscription.channel_id)
                .filter(Subscription.user_id == user_id, Subscription.is_active is True)
                .all()
            )
        except SQLAlchemyError as e:
            raise e

    def update_status(self, subscription: Subscription):
        try:
            subscription.is_active = True
            self.session.commit()
            return subscription
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e

    def delete(self, subscription: Subscription) -> bool:
        try:
            self.session.delete(subscription)
            self.session.commit()
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e


