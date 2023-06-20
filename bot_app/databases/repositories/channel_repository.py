from typing import Optional
from shared.database import async_session
from shared.models import Channel
from sqlalchemy.exc import SQLAlchemyError

from sqlalchemy.future import select


class ChannelRepository:
    async def create(self, **kwargs) -> Channel:
        try:
            async with async_session() as session:
                channel = Channel(**kwargs)
                session.add(channel)
                await session.commit()
                return channel
        except SQLAlchemyError as e:
            await session.rollback()
            raise e

    async def get(self, channel_username: str) -> Optional[Channel]:
        try:
            async with async_session() as session:
                stmt = select(Channel).where(Channel.channel_username == channel_username)
                result = await session.execute(stmt)
                return result.scalars().first()
        except SQLAlchemyError as e:
            raise e

    async def delete(self, channel: Channel):
        try:
            async with async_session() as session:
                session.delete(channel)
                await session.commit()
                return True
        except SQLAlchemyError as e:
            await session.rollback()
            raise e