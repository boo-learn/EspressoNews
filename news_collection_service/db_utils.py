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

