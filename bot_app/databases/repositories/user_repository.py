import logging
from typing import Optional, List
from shared.database import async_session
from shared.db_utils import get_role, get_intonation
from shared.models import User, UserSettings, BeatSchedule
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from sqlalchemy.future import select

logger = logging.getLogger(__name__)


class UserRepository:

    @staticmethod
    async def create(**kwargs) -> User:
        try:
            async with async_session() as session:
                user = User(**kwargs)
                user_settings = UserSettings()
                user.settings = user_settings
                user_settings.role = await get_role('Helpfull assistant.')
                user_settings.intonation = await get_intonation('Official')

                session.add(user)
                session.add(user_settings)
                await session.commit()

                return user
        except SQLAlchemyError as e:
            await session.rollback()
            raise e

    @staticmethod
    async def get(user_id: int) -> Optional[User]:
        try:
            async with async_session() as session:
                stmt = (select(User)
                        .options(joinedload(User.settings))
                        .options(
                    joinedload(User.settings).joinedload(UserSettings.intonation))  # Use joinedload for intonation
                        .options(joinedload(User.settings).joinedload(UserSettings.role))  # Use joinedload for role
                        .where(User.user_id == user_id))
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
                session.add(user)
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

    @staticmethod
    async def get_all_users_settings():
        try:
            async with async_session() as session:
                result = await session.execute(select(UserSettings))
                return result.scalars().all()
        except SQLAlchemyError as e:
            await session.rollback()
            raise e

    @staticmethod
    async def update_setting(settings: UserSettings, field: str, value) -> bool:
        try:
            async with async_session() as session:
                session.add(settings)
                setattr(settings, field, value)
                logging.info(f"Settings: {settings}, field {field}, mapped_value {value}")
                await session.commit()
                return True
        except SQLAlchemyError as e:
            logging.info(f"Rollback")
            await session.rollback()
            raise e

    @staticmethod
    async def get_user_settings(user_id: int) -> Optional[UserSettings]:
        try:
            async with async_session() as session:
                stmt = select(UserSettings).where(UserSettings.user_id == user_id)
                result = await session.execute(stmt)
                return result.scalars().first()
        except SQLAlchemyError as e:
            raise e

    @staticmethod
    async def delete_schedule(task_name: str) -> bool:
        try:
            async with async_session() as session:
                stmt = select(BeatSchedule).filter_by(task_name=task_name)
                result = await session.execute(stmt)
                schedule = result.scalars().first()
                if schedule:
                    await session.delete(schedule)
                    await session.commit()
                    return True
                else:
                    return False
        except SQLAlchemyError as e:
            await session.rollback()
            raise e

