import logging
from typing import Optional, List
from shared.database import async_session
from shared.models import User, UserSettings
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from sqlalchemy.future import select

from shared.selection_values_for_models import IntonationEnum, PeriodicityEnum, RoleEnum

logger = logging.getLogger(__name__)


class UserRepository:
    settings_value_mappings = {
        'Официальная': IntonationEnum.OFFICIAL,
        'Саркастично-шутливая': IntonationEnum.COMEDY_SARCASTIC,
        'Каждый час': PeriodicityEnum.HOURLY,
        'Каждые 3 часа': PeriodicityEnum.EVERY_THREE_HOURS,
        'Каждые 6 часов': PeriodicityEnum.EVERY_SIX_HOURS,
        'Диктор': RoleEnum.ANNOUNCER,
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
                logging.info(f"Field: {field}, value_mapping: {UserRepository.settings_value_mappings}")
                logging.info(value in UserRepository.settings_value_mappings)
                if value in UserRepository.settings_value_mappings:
                    session.add(settings)
                    mapped_value = UserRepository.settings_value_mappings[value]
                    setattr(settings, field, mapped_value)
                    logging.info(f"Settings: {settings}, field {field}, mapped_value {mapped_value}")
                    await session.commit()
                    return True
                else:
                    return False
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
