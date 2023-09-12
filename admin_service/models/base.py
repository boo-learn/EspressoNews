from typing import List
from shared.database import Base

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)


# class Permission(Base):
#     id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
#     rule = ...
#
# class PermissionGroup(Base):
#     id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
#     name: Mapped[str]
#     permissions: Mapped[List[Permission]] = ...


class AdminUserBase(Base):
    __tablename__ = "admin_users"
    # __table_args__ = {"schema": "myapi"}
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(unique=True)
    # email = Column(String, primary_key=True, index=True)
    name: Mapped[str]
    hashed_password: Mapped[str]
    role: Mapped[str]
