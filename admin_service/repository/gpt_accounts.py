from typing import Any
from fastapi import HTTPException, status

from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from admin_service import models, schemas


async def get_by_id(
        session: AsyncSession, *, id: int
) -> models.GPTAccount | None:
    return await session.get(models.GPTAccount, id)


async def get_multi(
        session: AsyncSession, *, skip: int = 0, limit: int = 100
) -> list[models.GPTAccount | None]:
    tg_accounts = await session.scalars(select(models.GPTAccount).offset(skip).limit(limit))
    return list(tg_accounts.all())


async def create(
        session: AsyncSession, *, obj_data: schemas.GPTAccountCreateSchema
) -> models.GPTAccount:
    db_obj = models.GPTAccount(**obj_data.model_dump())
    session.add(db_obj)
    await session.commit()
    await session.refresh(db_obj)
    return db_obj


async def update(
        session: AsyncSession, *,
        db_obj: models.GPTAccount,
        obj_data: schemas.GPTAccountUpdateSchema | dict[str, Any]
) -> models.GPTAccount:
    if isinstance(obj_data, dict):
        update_data: dict = obj_data
    else:
        update_data: dict = obj_data.model_dump(exclude_unset=True)
    for field in update_data:
        setattr(db_obj, field, update_data[field])
    session.add(db_obj)
    await session.commit()
    await session.refresh(db_obj)
    return db_obj


async def remove(
        session: AsyncSession, *, db_obj: models.GPTAccount
) -> None:
    await session.delete(db_obj)
    await session.commit()
