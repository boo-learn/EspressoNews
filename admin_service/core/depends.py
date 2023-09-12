from loguru import logger

from fastapi import (
    Depends,
    HTTPException,
    status
)
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.orm import (
    Session,
)
from sqlalchemy import exc
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from collections.abc import AsyncGenerator

from pydantic import ValidationError
from jose import jwt

from shared.database import DATABASE_URI

from admin_service import schemas, repository, crud
from admin_service.models.admin_user import AdminUser
from admin_service.core.config import settings
from admin_service.core import const


# def create_session() -> Generator[Session]:
#     """Create new SYNC database session.
#
#     Yields:
#         Database session.
#     """
#
#     session = SessionFactory()
#
#     try:
#         yield session
#         session.commit()
#     except Exception:
#         session.rollback()
#         raise
#     finally:
#         session.close()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(DATABASE_URI)
    factory = async_sessionmaker(engine)
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except exc.SQLAlchemyError as error:
            await session.rollback()
            raise


reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"/auth/login/access-token"
)


async def get_current_user(
        session: AsyncSession = Depends(get_db_session), token: str = Depends(reusable_oauth2)
) -> AdminUser:
    try:
        payload = jwt.decode(
            token, settings.token_key, algorithms=[const.TOKEN_ALGORITHM]
        )
        token_data = schemas.TokenCreateSchema(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = await crud.admin_user.get(session, id=token_data.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


from admin_service.permissions.base import ModelPermission
from admin_service.permissions.roles import get_role_permissions


class PermissionChecker:
    def __init__(self, permissions_required: list[ModelPermission]):
        self.permissions_required = permissions_required

    def __call__(self, user: AdminUser = Depends(get_current_user)):
        for permission_required in self.permissions_required:
            if permission_required not in get_role_permissions(user.role):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions to access this resource")
        return user
