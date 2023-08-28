from typing import Generator

from fastapi import (
    Depends,
    HTTPException
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

# create session factory to generate new database sessions
from shared.database import DATABASE_URI

from admin_service import models, schemas


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
    tokenUrl=f"/login/access-token"
)

# def get_current_user(
#         db: Session = Depends(create_session),
#         token: str = Depends(reusable_oauth2)
# ) -> models.AdminUser:
#     try:
#         payload = jwt.decode(
#             token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
#         )
#         token_data = schemas.TokenPayload(**payload)
#     except (jwt.JWTError, ValidationError):
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Could not validate credentials",
#         )
#     user = crud.user.get(db, id=token_data.sub)
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     return user
