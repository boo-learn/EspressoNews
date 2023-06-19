from sqlalchemy import select

from shared.database import async_session
from shared.models import TelegramAccount, Channel


async def get_account_from_db_async(account_id: int):
    async with async_session() as db:
        return await db.query(TelegramAccount).filter(TelegramAccount.account_id == account_id).first()


async def remove_account_from_db_async(account_id: int):
    async with async_session() as db:
        account = await db.query(TelegramAccount).filter(TelegramAccount.account_id == account_id).first()
        if account:
            db.delete(account)
            await db.commit()
            return True
    return False


async def get_subscribed_channels(client):
    dialogs = await client.get_dialogs()
    channels = [dialog.entity for dialog in dialogs if dialog.is_channel]
    return channels


async def get_first_active_account_from_db_async():
    async with async_session() as db:  # Replace SessionLocal() with async_session()
        return await db.query(TelegramAccount).filter(TelegramAccount.is_active == True).first()


async def get_unique_channel_ids_async():
    async with async_session() as db:  # Replace SessionLocal() with async_session()
        stmt = select(Channel.channel_id).distinct()
        result = await db.execute(stmt)
        channel_ids = result.scalars().all()
        return [channel_id for channel_id in channel_ids]