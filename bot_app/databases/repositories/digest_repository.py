from charset_normalizer.md import Optional
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from shared.database import async_session
from shared.models import Digest, Post


class DigestRepository:
    async def get(self, digest_id: int) -> Optional[Digest]:
        try:
            async with async_session() as session:
                stmt = (
                    select(Digest).options(
                        joinedload(Digest.posts).
                        joinedload(Post.summaries)
                    ).where(Digest.id == digest_id)
                )
                result = await session.execute(stmt)
                return result.scalars().first()
        except SQLAlchemyError as e:
            raise e
