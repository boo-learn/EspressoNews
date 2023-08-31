from shared.database import Base

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)


class AdminUserBase(Base):
    __tablename__ = "admin_users"
    # __table_args__ = {"schema": "myapi"}
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str]
    hashed_password: Mapped[str]
