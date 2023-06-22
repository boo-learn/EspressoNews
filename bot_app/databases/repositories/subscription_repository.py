from sqlalchemy import func
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
                stmt = (
                    select(Subscription)
                    .options(joinedload(Subscription.user), joinedload(Subscription.channel))
                    .filter_by(user_id=user_id, channel_id=channel.channel_id)
                )
                result = await session.execute(stmt)
                return result.scalars().first()
            except SQLAlchemyError as e:
                raise e

    async def get_channels_count(self, channel_id):
        async with async_session() as session:
            stmt = select(func.count()).select_from(Subscription).where(Subscription.channel_id == channel_id)
            count = await session.scalar(stmt)
            return count

    async def get_channels(self, user_id: int):
        async with async_session() as session:
            try:
                stmt = select(Channel).join(Subscription, Channel.channel_id == Subscription.channel_id).filter(
                    Subscription.user_id == user_id, Subscription.is_active == True
                )
                result = await session.execute(stmt)
                channels = result.fetchall()
                return channels
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
        print(subscription)
        async with async_session() as session:
            try:
                await session.delete(subscription)
                await session.commit()
                return True
            except SQLAlchemyError as e:
                await session.rollback()
                raise e
