from pydantic import (
    BaseModel,
    ValidationError,
)

from pydantic_settings import (
    BaseSettings,
)


# class DatabaseConfig(BaseModel):
#     db_host: str
#     db_port: int = 5432


# TODO: переписать общий конфиг проекта на Pydantic и использовать тут
class Settings(BaseSettings):
    # database: DatabaseConfig = DatabaseConfig()
    token_key: str = ""
    FIRST_SUPERUSER_NAME: str = "admin"
    FIRST_SUPERUSER_EMAIL: str = "admin@testmail.ru"
    FIRST_SUPERUSER_PASSWORD: str = "adminPasswrd"

    class Config:
        env_file = ".env.dev"
        env_file_encoding = "utf-8"
        # env_prefix = "MYAPI_"
        env_nested_delimiter = "__"
        case_sensitive = False
        extra = 'allow'


settings = Settings()
