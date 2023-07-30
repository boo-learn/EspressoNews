from random import choice

from sqlalchemy import select, func, delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload

from shared.database import async_session
from shared.models import TelegramAccount, Channel


async def get_telethon_accounts_list():
    try:
        async with async_session() as db:
            stmt = select(TelegramAccount).options(selectinload(TelegramAccount.channels))
            result = await db.execute(stmt)
            accounts = result.scalars().all()

            return accounts or None
    except SQLAlchemyError as e:
        raise e


async def delete_banned_account_and_reconnect_channels(banned_account_id, unlinked_channels):
    async with async_session() as db:
        try:
            # Disassociate the banned account from its channels
            channels = await db.execute(
                select(Channel)
                .where(Channel.account_id == banned_account_id)
            )
            channels = channels.scalars().all()
            for channel in channels:
                channel.account_id = None
                await db.merge(channel)

            # Flush the session to send the changes to the database
            await db.flush()

            # Delete the banned account
            await db.execute(
                delete(TelegramAccount)
                .where(TelegramAccount.account_id == banned_account_id)
            )

            # Commit the transaction
            await db.commit()
        except SQLAlchemyError as e:
            await db.rollback()
            raise e


async def remove_subscription(account_id: int, channel_username: str):
    async with async_session() as db:
        try:
            account = await db.get(TelegramAccount, account_id)
            channel = await db.execute(select(Channel).filter(Channel.channel_username == channel_username))
            channel = channel.scalars().first()
            if account and channel and channel.telegram_account == account:
                channel.telegram_account = None
                await db.commit()
        except SQLAlchemyError as e:
            await db.rollback()
