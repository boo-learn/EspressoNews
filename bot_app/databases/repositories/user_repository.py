import logging
from typing import Optional, List
from shared.database import async_session
from shared.db_utils import get_role, get_intonation, get_language
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
                user_settings.language = await get_language('English')

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
                            joinedload(User.settings).joinedload(UserSettings.intonation))
                        .options(
                            joinedload(User.settings).joinedload(UserSettings.role))
                        .options(
                            joinedload(User.settings).joinedload(UserSettings.language))
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
                result = await session.execute(
                    select(UserSettings)
                    .options(
                        joinedload(UserSettings.language),
                        joinedload(UserSettings.role),
                        joinedload(UserSettings.intonation)
                    )
                )
                return result.scalars().all()
        except SQLAlchemyError as e:
            await session.rollback()
            raise e

    @staticmethod
    async def update_setting(user_id: int, option: str, value) -> bool:
        async with async_session() as session:
            try:
                stmt = (select(User).options(joinedload(User.settings)).where(User.user_id == user_id))
                result = await session.execute(stmt)
                user = result.scalars().first()

                if not user:
                    return False

                settings = user.settings
                setattr(settings, option, value)
                await session.commit()
                return True
            except SQLAlchemyError as e:
                await session.rollback()
                raise e

    @staticmethod
    async def get_user_settings(user_id: int) -> Optional[UserSettings]:
        try:
            async with async_session() as session:
                stmt = (
                    select(UserSettings)
                    .options(
                        joinedload(UserSettings.role),
                        joinedload(UserSettings.intonation),
                        joinedload(UserSettings.language)
                    )
                    .where(UserSettings.user_id == user_id)
                )
                result = await session.execute(stmt)
                user_settings = result.scalars().first()
                return user_settings
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
