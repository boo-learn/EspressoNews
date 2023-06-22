from typing import Optional
from shared.database import async_session
from shared.models import User
from sqlalchemy.exc import SQLAlchemyError

from sqlalchemy.future import select


class UserRepository:
    async def create(self, **kwargs) -> User:
        try:
            async with async_session() as session:
                user = User(**kwargs)
                session.add(user)
                await session.commit()
                return user
        except SQLAlchemyError as e:
            await session.rollback()
            raise e

    async def get(self, user_id: int) -> Optional[User]:
        try:
            async with async_session() as session:
                stmt = select(User).where(User.user_id == user_id)
                result = await session.execute(stmt)
                return result.scalars().first()
        except SQLAlchemyError as e:
            raise e

    async def get_by_username(self, username: str) -> Optional[User]:
        try:
            async with async_session() as session:
                stmt = select(User).where(User.username == username)
                result = await session.execute(stmt)
                return result.scalars().first()
        except SQLAlchemyError as e:
            raise e

    async def update(self, user: User, **kwargs) -> User:
        try:
            async with async_session() as session:
                for key, value in kwargs.items():
                    setattr(user, key, value)
                await session.commit()
                return user
        except SQLAlchemyError as e:
            await session.rollback()
            raise e

    async def delete(self, user: User):
        try:
            async with async_session() as session:
                await session.delete(user)
                await session.commit()
                return True
        except SQLAlchemyError as e:
            await session.rollback()
            raise e
