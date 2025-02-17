from loguru import logger

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from admin_service.models.admin_user import AdminUser
from admin_service.core import depends
# from admin_service.core.depends import PermissionChecker
from admin_service.permissions import models_permissions
from admin_service.core.const import (
    USERS_TAGS,
)

from admin_service import repository, schemas, crud

router = APIRouter(prefix="", tags=USERS_TAGS)


@router.get("/users", response_model=list[schemas.UserSchema])
async def get_users(
        session: AsyncSession = Depends(depends.get_db_session),
        skip: int = 0,
        limit: int = 100,
):
    return await crud.admin_user.get_multi(session, skip=skip, limit=limit)


@router.get("/users/{id}", response_model=schemas.UserSchema)
async def get_user_by_id(
        id: int,
        session: AsyncSession = Depends(depends.get_db_session),
):
    user = await crud.admin_user.get(session, id=id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id={id} does not exist",
        )
    return user


@router.post("/users", response_model=schemas.UserSchema, status_code=201)
async def create_user(
        user_data: schemas.UserCreateSchema,
        session: AsyncSession = Depends(depends.get_db_session),
        permission=Depends(depends.PermissionChecker([models_permissions.AdminUsers.permissions.CREATE]))
):
    user = await crud.admin_user.get_by_email(session, email=user_data.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this username already exists in the system.",
        )
    user = await crud.admin_user.create(session, obj_data=user_data)
    return user
