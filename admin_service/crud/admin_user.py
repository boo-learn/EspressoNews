from typing import Any, Dict, Optional, Union

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)
from sqlalchemy import select

from admin_service.crud.base import CRUDBase
from admin_service.models.admin_user import AdminUser
from admin_service import schemas


class CRUDAdminUser(CRUDBase[AdminUser, schemas.UserCreateSchema, schemas.UserUpdateSchema]):
    async def get_by_email(self, session: AsyncSession, *, email: str) -> AdminUser | None:
        return await session.scalar(select(AdminUser).where(AdminUser.email == email))

    # def update(
    #         self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    # ) -> User:
    #     if isinstance(obj_in, dict):
    #         update_data = obj_in
    #     else:
    #         update_data = obj_in.dict(exclude_unset=True)
    #     if update_data["password"]:
    #         hashed_password = get_password_hash(update_data["password"])
    #         del update_data["password"]
    #         update_data["hashed_password"] = hashed_password
    #     return super().update(db, db_obj=db_obj, obj_in=update_data)

    # def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
    #     user = self.get_by_email(db, email=email)
    #     if not user:
    #         return None
    #     if not verify_password(password, user.hashed_password):
    #         return None
    #     return user


admin_user = CRUDAdminUser(AdminUser)
