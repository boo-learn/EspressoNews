from shared.database import async_session
from shared.models import Post


async def add_post_async(post: Post):
    async with async_session() as db:
        db.add(post)
        await db.commit()
        await db.refresh(post)
        return post


async def get_subscribed_channels(client):
    dialogs = await client.get_dialogs()
    channels = [dialog.entity for dialog in dialogs if dialog.is_channel]
    return channels

