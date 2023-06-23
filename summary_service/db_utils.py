from sqlalchemy.orm import Session, joinedload

from shared.models import Post, GPTAccount
from shared.database import async_session


async def get_posts_without_summary_async(limit: int = 50):
    async with async_session() as db:
        result = await db.query(Post).options(
            joinedload(Post.channel),
            joinedload(Post.rubric),
            joinedload(Post.files)
        ).filter(Post.summary is None).limit(limit).all()

        return result.scalars().all()


async def update_post_summary_async(post_id: int, summary: str):
    async with async_session() as db:
        post = await db.query(Post).filter(Post.post_id == post_id).one()
        post.summary = summary
        await db.commit()


async def get_active_gpt_accounts_async():
    async with async_session() as db:
        result = await db.query(GPTAccount).filter(GPTAccount.is_active is True).all()
        return result.scalars().all()
