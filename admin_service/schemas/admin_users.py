from pydantic import BaseModel, EmailStr


class BaseUserSchema(BaseModel):
    name: str
    email: EmailStr


class CreateUserSchema(BaseUserSchema):
    password: str


class UserSchema(BaseUserSchema):
    id: int
