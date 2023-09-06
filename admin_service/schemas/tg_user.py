from datetime import datetime
from pydantic import BaseModel

from shared.models import User, Category
from admin_service.schemas import CategorySchema


class BaseTgUserSchema(BaseModel):
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    language_code: str | None = None
    is_active: bool
    join_date: datetime
    disabled_at: datetime | None = None


class TgUserSchema(BaseTgUserSchema):
    user_id: int
    categories: list[CategorySchema]
