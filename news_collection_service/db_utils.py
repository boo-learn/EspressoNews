from sqlalchemy.orm import joinedload

from shared.models import Channel
from sqlalchemy import select

from shared.database import async_session
from shared.models import Post


async def add_post_async(post: Post):
    async with async_session() as db:
        post = await db.merge(post)
        await db.commit()
        return post


async def get_subscribed_channels(client):
    dialogs = await client.get_dialogs()
    channels = [dialog.entity for dialog in dialogs if dialog.is_channel and dialog.entity.username]
    return channels


async def get_all_channels():
    async with async_session() as session:
        result = await session.execute(select(Channel))
        channels = result.scalars().all()
        return channels


async def get_channels_by_account_id(account_id: int):
    async with async_session() as db:
        result = await db.execute(
            select(Channel).options(joinedload(Channel.telegram_account)).filter(Channel.account_id == account_id)
        )
        channels = result.scalars().all()
        return channels
