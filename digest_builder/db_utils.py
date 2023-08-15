from sqlalchemy import select, tuple_, and_, not_, exists
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, joinedload, aliased

from shared.models import Post, GPTAccount, Role, Intonation, Summary
from shared.database import async_session

from sqlalchemy import select
from sqlalchemy.orm import joinedload


async def update_post_summary_async(session, post_id: int, summary: str, role_id: str, intonation_id: int):
    new_summary = Summary(content=summary, role_id=role_id, intonation_id=intonation_id, post_id=post_id)
    session.add(new_summary)


async def get_active_gpt_accounts_async(session):
    result = await session.execute(select(GPTAccount).where(GPTAccount.is_active == True))
    return result.scalars().all()


async def update_chatgpt_account_async(api_key: str):
    async with async_session() as db:
        result = await db.execute(
            select(GPTAccount).where(GPTAccount.api_key == api_key)
        )
        acc = result.scalar_one()
        acc.is_active = False
        await db.commit()
