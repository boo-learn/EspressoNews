from pydantic import BaseModel, EmailStr


class TokenSchema(BaseModel):
    access_token: str
    token_type: str


class TokenCreateSchema(BaseModel):
    user_id: int | None = None
