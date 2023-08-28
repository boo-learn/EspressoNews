from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from datetime import (
    datetime,
    timedelta,
)

from passlib.context import CryptContext
from jose import jwt

from admin_service.core.config import settings
from admin_service.core import const
from shared.database import Base

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AdminUser(Base):
    __tablename__ = "admin_users"
    # __table_args__ = {"schema": "myapi"}
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # TODO: email --> unique
    email: Mapped[str]
    name: Mapped[str]
    hashed_password: Mapped[str]

    def __init__(self, **kwargs):
        hashed_password = AdminUser.get_password_hash(kwargs["password"])
        del kwargs["password"]
        kwargs["hashed_password"] = hashed_password
        super().__init__(**kwargs)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    def create_access_token(self) -> str:
        """Encode user information and expiration time."""

        payload = {
            "name": self.name,
            "sub": self.email,
            "expires_at": self._expiration_time(),
        }

        return jwt.encode(payload, settings.token_key, algorithm=const.TOKEN_ALGORITHM)

    @staticmethod
    def _expiration_time() -> str:
        """Get token expiration time."""

        expires_at = datetime.utcnow() + timedelta(minutes=const.TOKEN_EXPIRE_MINUTES)
        return expires_at.strftime("%Y-%m-%d %H:%M:%S")
