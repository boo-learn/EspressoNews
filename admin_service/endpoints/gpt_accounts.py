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
    GPTACCOUNTS_URL,
    GPTACCOUNTS_TAGS
)

from admin_service import repository, schemas
from admin_service.models.admin_user import AdminUser

router = APIRouter(prefix="" + GPTACCOUNTS_URL, tags=GPTACCOUNTS_TAGS)


@router.get("", response_model=list[schemas.GPTAccountSchema])
async def get_gpt_accounts(
        session: AsyncSession = Depends(depends.get_db_session),
        skip: int = 0,
        limit: int = 100,
):
    db_object = await repository.gpt_accounts.get_multi(session, skip=skip, limit=limit)
    if db_object is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id={id} does not exist",
        )
    return db_object


@router.get("/{id}", response_model=schemas.GPTAccountSchema)
async def get_gpt_account_by_ig(
        id: int,
        session: AsyncSession = Depends(depends.get_db_session),
):
    db_object = await repository.gpt_accounts.get_by_id(session, id=id)
    if db_object is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Telegram Account with id={id} does not exist",
        )
    return db_object


@router.post("", response_model=schemas.GPTAccountSchema)
async def create_gpt_account(
        gpt_account_data: schemas.GPTAccountCreateSchema,
        session: AsyncSession = Depends(depends.get_db_session),
        current_user: AdminUser = Depends(depends.get_current_user)
):
    db_object = await repository.gpt_accounts.create(session, obj_data=gpt_account_data)
    return db_object


@router.put("/{id}", response_model=schemas.GPTAccountSchema)
async def update_gpt_account(
        id: int,
        gpt_account_data: schemas.GPTAccountUpdateSchema,
        session: AsyncSession = Depends(depends.get_db_session),
        current_user: AdminUser = Depends(depends.get_current_user)
):
    db_object = await repository.gpt_accounts.get_by_id(session, id=id)
    if not db_object:
        raise HTTPException(status_code=404, detail=f"Telegram Account with id={id} does not exist")
    db_object = await repository.gpt_accounts.update(session, db_obj=db_object, obj_data=gpt_account_data)
    return db_object


@router.delete("/{id}", status_code=204)
async def delete_gpt_account(
        id: int,
        session: AsyncSession = Depends(depends.get_db_session),
        current_user: AdminUser = Depends(depends.get_current_user)
):
    db_object = await repository.gpt_accounts.get_by_id(session, id=id)
    if not db_object:
        raise HTTPException(status_code=404, detail=f"Telegram Account with id={id} does not exist")
    await repository.gpt_accounts.remove(session, db_obj=db_object)
