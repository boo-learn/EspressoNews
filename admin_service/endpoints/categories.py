from loguru import logger

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from admin_service.core import depends
from admin_service.core.const import (
    CATEGORIES_URL,
    CATEGORIES_TAGS
)

from admin_service import crud, schemas
from admin_service.models.admin_user import AdminUser
from admin_service.core.depends import PermissionChecker
from admin_service.permissions import models_permissions
from shared.models import Category

router = APIRouter(prefix="" + CATEGORIES_URL, tags=CATEGORIES_TAGS)


@router.get("", response_model=list[schemas.CategorySchema])
async def get_categories(
        session: AsyncSession = Depends(depends.get_db_session),
        skip: int = 0,
        limit: int = 100,
):
    db_object = await crud.category.get_multi(session, skip=skip, limit=limit)
    if db_object is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id={id} does not exist",
        )
    return db_object


@router.get("/{id}", response_model=schemas.CategorySchema)
async def get_category_by_id(
        id: int,
        session: AsyncSession = Depends(depends.get_db_session),
):
    db_object = await crud.category.get(session, id=id)
    if db_object is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Telegram Account with id={id} does not exist",
        )
    return db_object


@router.post("", response_model=schemas.CategorySchema)
async def create_category(
        category_data: schemas.CategoryCreateSchema,
        session: AsyncSession = Depends(depends.get_db_session),
        permission=Depends(PermissionChecker([models_permissions.Categories.permissions.CREATE])),
):
    db_object = await crud.category.create(session, obj_data=category_data)
    return db_object


@router.put("/{id}", response_model=schemas.CategorySchema)
async def update_category(
        id: int,
        category_data: schemas.CategoryUpdateSchema,
        session: AsyncSession = Depends(depends.get_db_session),
        permission=Depends(PermissionChecker([models_permissions.Categories.permissions.UPDATE]))
):
    db_object = await crud.category.get(session, id=id)
    if not db_object:
        raise HTTPException(status_code=404, detail=f"Telegram Account with id={id} does not exist")
    db_object = await crud.category.update(session, db_obj=db_object, obj_data=category_data)
    return db_object


from sqlalchemy import select
from sqlalchemy.orm import selectinload


@router.put("/{id}/users", status_code=204)
async def add_relationship(
        id: int,  # category_id
        user_ids: list[int],
        session: AsyncSession = Depends(depends.get_db_session),
        permission=Depends(PermissionChecker([models_permissions.Categories.permissions.UPDATE]))
):
    category = await crud.category.get(session, id=id)
    # TODO: move to CRUD or lazy='joined'
    # result = await session.scalars(
    #     select(Category).where(Category.id == id).options(selectinload(Category.category_recs))
    # )
    # category = result.unique().first()
    if not category:
        raise HTTPException(status_code=404, detail=f"Telegram Account with id={id} does not exist")
    try:
        await crud.category.relation_with_users(session, category=category, user_ids=user_ids)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has this category")


@router.delete("/{id}", status_code=204)
async def delete_category(
        id: int,
        session: AsyncSession = Depends(depends.get_db_session),
        permission=Depends(PermissionChecker([models_permissions.Categories.permissions.DELETE]))
):
    db_object = await crud.category.get(session, id=id)
    if not db_object:
        raise HTTPException(status_code=404, detail=f"Category with id={id} does not exist")
    await crud.category.remove(session, db_obj=db_object)
