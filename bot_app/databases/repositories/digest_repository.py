from charset_normalizer.md import Optional
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from shared.database import async_session
from shared.models import Digest, Post, UserSettings


class DigestRepository:
    async def get(self, digest_id: int) -> Optional[Digest]:
        try:
            async with async_session() as session:
                stmt = (
                    select(Digest).options(
                        joinedload(Digest.posts).
                        joinedload(Post.summaries),
                        joinedload(Digest.posts).
                        joinedload(Post.channel)
                    ).where(Digest.id == digest_id)
                )
                result = await session.execute(stmt)
                return result.scalars().first()
        except SQLAlchemyError as e:
            raise e

    async def create(self, user_id: int):
        try:
            async with async_session() as session:
                digest = Digest(
                    user_id=user_id,
                    role_id=1,
                    intonation_id=1,
                    is_active=True
                )
                session.add(digest)
                await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()
            raise e

    async def update(self, digest: Digest, **kwargs) -> Digest:
        try:
            async with async_session() as session:
                for key, value in kwargs.items():
                    setattr(digest, key, value)
                session.add(digest)
                await session.commit()
                return digest
        except SQLAlchemyError as e:
            await session.rollback()
            raise e

    async def clear(self, digest: Digest):
        try:
            async with async_session() as session:
                digest_result = await session.execute(
                    select(Digest).filter(Digest.id == digest.id).options(
                        joinedload(Digest.digest_recs))
                )
                digest = digest_result.unique().scalar_one_or_none()
                digest.digest_ids.clear()
                await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()
            raise e

    async def change_digest(self, digest: Digest, user_id: int):
        try:
            async with async_session() as session:
                session.add(digest)
                digest.is_active = False
                result = await session.execute(
                    select(UserSettings)
                    .options(joinedload(UserSettings.role), joinedload(UserSettings.intonation))
                    .filter(UserSettings.user_id == user_id)
                )
                user_settings = result.scalars().first()
                new_digest = Digest(
                    user_id=user_id,
                    role_id=user_settings.role_id,
                    intonation_id=user_settings.intonation_id,
                    is_active=True
                )
                session.add(new_digest)
                await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()
            raise e
