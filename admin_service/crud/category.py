from typing import Any, Dict, Optional, Union

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)
from sqlalchemy import select

from admin_service.crud.base import CRUDBase
from shared.models import Category
from admin_service import schemas


class CRUDTgAccount(CRUDBase[Category, schemas.CategoryCreateSchema, schemas.CategoryUpdateSchema]):
    async def relation_with_users(self, session: AsyncSession, category: Category, user_ids: list[int]):
        category.user_ids.extend(user_ids)
        session.add(category)
        await session.commit()


category = CRUDTgAccount(Category)
