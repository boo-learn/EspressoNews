from pydantic import BaseModel, EmailStr
from admin_service.permissions.roles import Role


class BaseUserSchema(BaseModel):
    name: str
    email: EmailStr
    # TODO: add examples(https://fastapi.tiangolo.com/tutorial/schema-extra-example/)
    role: Role


class UserCreateSchema(BaseUserSchema):
    password: str


class UserSchema(BaseUserSchema):
    id: int


class UserUpdateSchema(BaseUserSchema):
    pass
