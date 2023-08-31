from pydantic import BaseModel, EmailStr
from shared.models import GPTAccount


class BaseGPTAccountSchema(BaseModel):
    api_key: str
    is_active: bool = True


class GPTAccountSchema(BaseGPTAccountSchema):
    account_id: int


class GPTAccountCreateSchema(BaseGPTAccountSchema):
    pass


class GPTAccountUpdateSchema(BaseModel):
    api_key: str | None = None
    is_active: bool | None = None
