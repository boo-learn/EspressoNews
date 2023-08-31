from loguru import logger

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy.ext.asyncio import AsyncSession

from admin_service.core import depends
from admin_service.core.const import (
    USERS_TAGS,
)

from admin_service import models, repository, schemas

router = APIRouter(prefix="", tags=...)


@router.get("/...", response_model=schemas)
async def func_name(
        session: AsyncSession = Depends(depends.get_db_session),
):
    db_object = await repository
    if db_object is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id={id} does not exist",
        )
    return db_object


# with Auth
@router.get("/...", response_model=schemas)
async def func_name(
        session: AsyncSession = Depends(depends.get_db_session),
        current_user: models.AdminUser = Depends(depends.get_current_user)
):
    db_object = await repository
    return db_object
