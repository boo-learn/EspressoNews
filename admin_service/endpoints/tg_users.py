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
    TGUSERS_URL,
    TGUSERS_TAGS
)

from admin_service import crud, schemas
from admin_service.models.admin_user import AdminUser

router = APIRouter(prefix="" + TGUSERS_URL, tags=TGUSERS_TAGS)


@router.get("", response_model=list[schemas.TgUserSchema])
async def get_tg_accounts(
        session: AsyncSession = Depends(depends.get_db_session),
        skip: int = 0,
        limit: int = 100,
):
    db_object = await crud.tg_user.get_multi(session, skip=skip, limit=limit)
    if db_object is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id={id} does not exist",
        )
    return db_object


@router.get("/{id}", response_model=schemas.TgUserSchema)
async def get_tg_account_by_id(
        id: int,
        session: AsyncSession = Depends(depends.get_db_session),
):
    db_object = await crud.tg_user.get(session, id=id)
    if db_object is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Telegram Account with id={id} does not exist",
        )
    return db_object
