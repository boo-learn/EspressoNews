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

from admin_service import models, schemas, repository
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
) -> models.AdminUser:
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
    user = await repository.admin_users.get_by_id(session, id=token_data.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
