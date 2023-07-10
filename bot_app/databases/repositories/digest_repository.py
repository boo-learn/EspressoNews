from charset_normalizer.md import Optional
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from shared.database import async_session
from shared.models import Digest


class DigestRepository:
    async def get(self, digest_id: int) -> Optional[Digest]:
        try:
            async with async_session() as session:
                stmt = (
                    select(Digest)
                    .where(Digest.id == digest_id)
                )
                result = await session.execute(stmt)
                return result.scalars().first()
        except SQLAlchemyError as e:
            raise e
