from typing import Optional, List
from shared.database import async_session
from shared.models import User, UserSettings
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from sqlalchemy.future import select

from shared.selection_values_for_models import IntonationEnum, PeriodicityEnum, RoleEnum


class UserRepository:
    settings_value_mappings = {
        'Официальная': IntonationEnum.OFFICIAL.value,
        'Саркастично-шутливая': IntonationEnum.COMEDY_SARCASTIC.value,
        'Каждый час': PeriodicityEnum.HOURLY.value,
        'Каждые 3 часа': PeriodicityEnum.EVERY_THREE_HOURS.value,
        'Каждые 6 часов': PeriodicityEnum.EVERY_SIX_HOURS.value,
        'Диктор': RoleEnum.ANNOUNCER.value,
    }

    @staticmethod
    async def create(**kwargs) -> User:
        try:
            async with async_session() as session:
                user = User(**kwargs)
                user_settings = UserSettings()
                user.settings = user_settings

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
                stmt = select(User).options(joinedload(User.settings)).where(User.user_id == user_id)
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
                if field in UserRepository.settings_value_mappings:
                    mapped_value = UserRepository.settings_value_mappings[value]
                    setattr(settings, field, mapped_value)
                    await session.commit()
                    return True
                else:
                    return False
        except SQLAlchemyError as e:
            await session.rollback()
            raise e
