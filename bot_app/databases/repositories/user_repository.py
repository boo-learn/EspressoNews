from typing import Optional, List
from shared.database import async_session
from shared.models import User
from sqlalchemy.exc import SQLAlchemyError

from sqlalchemy.future import select


class UserRepository:
    @staticmethod
    async def create(**kwargs) -> User:
        try:
            async with async_session() as session:
                user = User(**kwargs)
                session.add(user)
                await session.commit()
                return user
        except SQLAlchemyError as e:
            await session.rollback()
            raise e

    @staticmethod
    async def get(user_id: int) -> Optional[User]:
        try:
            async with async_session() as session:
                stmt = select(User).where(User.user_id == user_id)
                result = await session.execute(stmt)
                return result.scalars().first()
        except SQLAlchemyError as e:
            raise e

    @staticmethod
    async def get_all() -> List[Optional[User]]:
        try:
            async with async_session() as session:
                stmt = select(User)
                result = await session.execute(stmt)
                return result.scalars().all()
        except SQLAlchemyError as e:
            raise e

    @staticmethod
    async def get_by_username(username: str) -> Optional[User]:
        try:
            async with async_session() as session:
                stmt = select(User).where(User.username == username)
                result = await session.execute(stmt)
                return result.scalars().first()
        except SQLAlchemyError as e:
            raise e

    @staticmethod
    async def update(user: User, **kwargs) -> User:
        try:
            async with async_session() as session:
                for key, value in kwargs.items():
                    setattr(user, key, value)
                await session.commit()
                return user
        except SQLAlchemyError as e:
            await session.rollback()
            raise e

    @staticmethod
    async def delete(user: User):
        try:
            async with async_session() as session:
                await session.delete(user)
                await session.commit()
                return True
        except SQLAlchemyError as e:
            await session.rollback()
            raise e
