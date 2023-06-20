from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

from shared.database import async_session
from shared.models import Subscription, Channel

from sqlalchemy.future import select


class SubscriptionRepository:
    async def create(self, user_id: int, channel: Channel) -> Subscription:
        async with async_session() as session:
            try:
                subscription = Subscription(user_id=user_id, channel_id=channel.channel_id)
                session.add(subscription)
                await session.commit()
                return subscription
            except SQLAlchemyError as e:
                await session.rollback()
                raise e

    async def get(self, user_id: int, channel: Channel):
        async with async_session() as session:
            try:
                result = await session.execute(
                    select(Subscription)
                    .options(
                        joinedload(Subscription.user),
                        joinedload(Subscription.channel)
                    )
                    .filter_by(
                        user_id=user_id,
                        channel_id=channel.channel_id
                    )
                )
                return result.scalar_one_or_none()
            except SQLAlchemyError as e:
                raise e

    async def get_channels_count(self, channel_id):
        async with async_session() as session:
            return await select(Subscription).filter(Subscription.channel_id == channel_id).count().scalar_one_or_none(
                session)

    async def get_channels(self, user_id: int):
        async with async_session() as session:
            try:
                return (
                    await select(Channel)
                    .join(Subscription, Channel.channel_id == Subscription.channel_id)
                    .filter(Subscription.user_id == user_id, Subscription.is_active is True)
                    .all()
                )
            except SQLAlchemyError as e:
                raise e

    async def update_status(self, subscription: Subscription):
        async with async_session() as session:
            try:
                subscription.is_active = True
                await session.commit()
                return subscription
            except SQLAlchemyError as e:
                await session.rollback()
                raise e

    async def delete(self, subscription: Subscription) -> bool:
        async with async_session() as session:
            try:
                session.delete(subscription)
                await session.commit()
                return True
            except SQLAlchemyError as e:
                await session.rollback()
                raise e
