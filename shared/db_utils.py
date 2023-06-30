from sqlalchemy import select

from shared.database import async_session, sync_session
from shared.models import TelegramAccount, Channel


async def get_account_from_db_async(account_id: int):
    async with async_session() as db:
        result = await db.execute(select(TelegramAccount).filter(TelegramAccount.account_id == account_id))
        return result.scalars().first()


def get_account_from_db(account_id: int):
    with sync_session() as db:
        result = db.execute(select(TelegramAccount).filter(TelegramAccount.account_id == account_id))
        return result.scalars().first()
    

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
    async with async_session() as db:
        result = await db.execute(select(TelegramAccount).filter(TelegramAccount.is_active == True))
        return result.scalars().first()


async def get_unique_channel_ids_async():
    async with async_session() as db:
        stmt = select(Channel.channel_id).distinct()
        result = await db.execute(stmt)
        channel_ids = result.scalars().all()
        return [channel_id for channel_id in channel_ids]


async def get_channel_name_by_id(channel_id):
    async with async_session() as db:
        result = await db.execute(select(Channel).filter(Channel.channel_id == channel_id))
        channel = result.scalars().first()
        return channel.channel_username if channel else None