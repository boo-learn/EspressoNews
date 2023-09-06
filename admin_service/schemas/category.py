from pydantic import BaseModel, EmailStr
from shared.models import TelegramAccount


class BaseCategorySchema(BaseModel):
    name: str


class CategorySchema(BaseCategorySchema):
    id: int


class CategoryCreateSchema(BaseCategorySchema):
    pass


class CategoryUpdateSchema(BaseModel):
    name: str | None = None
