from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)
from sqlalchemy import select

from shared.database import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    async def get(self, session: AsyncSession, id: Any) -> Optional[ModelType]:
        return await session.get(self.model, id)

    async def get_multi(
            self, session: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        users = await session.scalars(select(self.model).offset(skip).limit(limit))
        return list(users.all())

    async def create(self, session: AsyncSession, *, obj_data: CreateSchemaType) -> ModelType:
        db_obj = self.model(**obj_data.model_dump())
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def update(
            self,
            session: AsyncSession,
            *,
            db_obj: ModelType,
            obj_data: UpdateSchemaType | dict[str, Any]
    ) -> ModelType:
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

    async def remove(self, session: AsyncSession, *, db_obj: ModelType):
        await session.delete(db_obj)
        await session.commit()
