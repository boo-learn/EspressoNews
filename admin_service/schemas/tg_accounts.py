from pydantic import BaseModel, EmailStr
from shared.models import TelegramAccount


class BaseTgAccountSchema(BaseModel):
    api_id: int
    api_hash: str
    phone_number: str
    session_string: str | None = None
    is_active: bool = True


class TgAccountSchema(BaseTgAccountSchema):
    account_id: int


class TgAccountCreateSchema(BaseTgAccountSchema):
    pass


class TgAccountUpdateSchema(BaseModel):
    api_id: int | None = None
    api_hash: str | None = None
    phone_number: str | None = None
    session_string: str | None = None
    is_active: bool | None = None
