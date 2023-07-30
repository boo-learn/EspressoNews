from sqlalchemy import select, tuple_, and_, not_, exists
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, joinedload, aliased

from shared.models import Post, GPTAccount, Role, Intonation, Summary
from shared.database import async_session

from sqlalchemy import select
from sqlalchemy.orm import joinedload


async def get_posts_without_summary_async(role_obj: Role = None, intonation_obj: Intonation = None, limit: int = None):
    async with async_session() as db:
        # Prepare subquery to fetch Post-Summary pairs
        post_summary_pairs = (
            select(Summary.post_id)
            .where(
                and_(
                    Summary.role_id == role_obj.id,
                    Summary.intonation_id == intonation_obj.id
                )
            )
        ).subquery()

        # Query for Posts that don't have a summary for the current combination
        posts_query = (
            select(Post)
            .options(joinedload(Post.channel))  # Load channel eagerly
            .where(
                ~Post.post_id.in_(post_summary_pairs)
            )
        )

        if limit is not None:
            posts_query = posts_query.limit(limit)

        result = await db.execute(posts_query)

        return result.scalars().all()


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


async def get_summary_for_post_async(post_id: int, role_id: int, intonation_id: int):
    async with async_session() as db:
        result = await db.execute(
            select(Summary).where(
                and_(
                    Summary.post_id == post_id,
                    Summary.role_id == role_id,
                    Summary.intonation_id == intonation_id
                )
            )
        )
        return result.scalars().first()  # Return the first matching summary, or None if no match is found


async def get_role_by_id(role_id: int):
    try:
        async with async_session() as session:
            result = await session.execute(select(Role).filter(Role.id == role_id))
            return result.scalars().first()
    except SQLAlchemyError as e:
        await session.rollback()
        raise e


async def get_intonation_by_id(intonation_id: int):
    try:
        async with async_session() as session:
            result = await session.execute(select(Intonation).filter(Intonation.id == intonation_id))
            return result.scalars().first()
    except SQLAlchemyError as e:
        await session.rollback()
        raise e
