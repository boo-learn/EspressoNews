from datetime import (
    datetime,
    timedelta,
)

from fastapi import (
    Depends,
    status,
)
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
)
from jose import (
    jwt,
    JWTError,
)
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from admin_service.core.config import settings
from admin_service.core.const import (
    AUTH_URL,
    TOKEN_ALGORITHM,
    TOKEN_EXPIRE_MINUTES,
    TOKEN_TYPE,
)
from admin_service import schemas, repository
from admin_service.models.admin_user import AdminUser

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_schema = OAuth2PasswordBearer(tokenUrl=AUTH_URL, auto_error=False)


async def authenticate(
        session: AsyncSession, *, email: str, password: str
) -> AdminUser | None:
    user = await repository.admin_users.get_by_email(session, email=email)
    if not user:
        return None
    if not user.verify_password(password, user.hashed_password):
        return None
    return user
