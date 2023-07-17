from sqlalchemy.orm import selectinload, joinedload
from telethon.tl.functions.channels import JoinChannelRequest, LeaveChannelRequest
from sqlalchemy import select, func, and_

from shared.database import async_session
from shared.models import TelegramAccount, Channel


async def subscribe_to_channel(client, channel_username):
    channel_entity = await client.get_input_entity(channel_username)
    await client(JoinChannelRequest(channel=channel_entity))


async def unsubscribe_from_channel(client, channel_username):
    channel_entity = await client.get_input_entity(channel_username)
    await client(LeaveChannelRequest(channel=channel_entity))


async def get_account_with_least_subscriptions():
    async with async_session() as db:
        stmt = (
            select(TelegramAccount)
            .options(selectinload(TelegramAccount.channels))
            .outerjoin(Channel, TelegramAccount.account_id == Channel.account_id)
            .group_by(TelegramAccount.account_id)
            .order_by(func.count(Channel.channel_id).asc())
        )
        result = await db.execute(stmt)
        return result.scalars().first()


async def add_subscription(account_id: int, channel_username: str):
    async with async_session() as db:
        account = await db.get(TelegramAccount, account_id)
        channel = await db.execute(select(Channel).filter(Channel.channel_username == channel_username))
        channel = channel.scalars().first()
        if account and channel:
            channel.telegram_account = account
            await db.commit()


async def is_have_subscription(channel_username: str):
    async with async_session() as db:
        result = await db.execute(select(Channel).options(joinedload(Channel.telegram_account)).filter(Channel.channel_username == channel_username))
        channel = result.scalars().first()
        if channel and channel.telegram_account is not None:
            return True
        else:
            return False