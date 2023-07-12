from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from shared.models import Post, GPTAccount
from shared.database import async_session

from sqlalchemy import select
from sqlalchemy.orm import joinedload


async def get_posts_without_summary_async(limit: int = 50):
    async with async_session() as db:
        result = await db.execute(
            select(Post).options(
                joinedload(Post.channel),
                joinedload(Post.rubric),
                joinedload(Post.files)
            ).where(Post.summary.is_(None)).limit(limit)
        )

        return result.unique().scalars().all()


async def update_post_summary_async(post_id: int, summary: str):
    async with async_session() as db:
        result = await db.execute(
            select(Post).where(Post.post_id == post_id)
        )
        post = result.scalar_one()
        post.summary = summary
        await db.commit()


async def get_active_gpt_accounts_async():
    async with async_session() as db:
        result = await db.execute(select(GPTAccount).where(GPTAccount.is_active == True))
        return result.scalars().all()


async def update_chatgpt_account_async(api_key: str):
    async with async_session() as db:
        result = await db.execute(
            select(GPTAccount).where(GPTAccount.api_key == api_key)
        )
        acc = result.scalar_one()
        acc.is_active = False
        await db.commit()
