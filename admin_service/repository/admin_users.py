from fastapi import HTTPException, status

from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from admin_service import models, schemas


async def get_by_id(
        db: AsyncSession, *, id: int
) -> models.AdminUser | None:
    return await db.get(models.AdminUser, id)
    # return db.scalar(select(models.AdminUser).where(models.AdminUser.id == id))


async def get_by_email(
        session: AsyncSession, *, email: str
) -> models.AdminUser | None:
    return await session.scalar(select(models.AdminUser).where(models.AdminUser.email == email))


async def get_multi(
        session: AsyncSession, *, skip: int = 0, limit: int = 100
) -> list[models.AdminUser | None]:
    users = await session.scalars(select(models.AdminUser).offset(skip).limit(limit))
    return list(users.all())


async def create(
        session: AsyncSession, *, obj_data: schemas.CreateUserSchema
) -> models.AdminUser:
    # obj_in_data = jsonable_encoder(obj_data)
    db_obj = models.AdminUser(**obj_data.model_dump())
    session.add(db_obj)
    await session.commit()
    await session.refresh(db_obj)
    return db_obj

# def update(
#  db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
# ) -> models.AdminUser:
