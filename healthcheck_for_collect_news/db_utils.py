from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload

from shared.database import async_session
from shared.models import TelegramAccount


async def get_telethon_accounts_list():
    try:
        async with async_session() as db:
            stmt = select(TelegramAccount).options(selectinload(TelegramAccount.channels))
            result = await db.execute(stmt)
            accounts = result.scalars().all()

            return accounts or None
    except SQLAlchemyError as e:
        raise e
