from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, joinedload

from shared.models import Post, GPTAccount, Role, Intonation, Summary
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


async def update_post_summary_async(post_id: int, summary: str, role_id: str, intonation_id: int):
    async with async_session() as db:
        new_summary = Summary(content=summary, role_id=role_id, intonation_id=intonation_id, post_id=post_id)
        db.add(new_summary)
        return await db.commit()


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


async def get_role_settings_options_for_gpt():
    try:
        async with async_session() as session:
            stmt = select(Role)
            result = await session.execute(stmt)
            return [row for row in result.scalars().all()]
    except SQLAlchemyError as e:
        raise e


async def get_intonation_settings_options_for_gpt():
    try:
        async with async_session() as session:
            stmt = select(Intonation)
            result = await session.execute(stmt)
            return [row for row in result.scalars().all()]
    except SQLAlchemyError as e:
        raise e
