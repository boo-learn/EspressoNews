from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from shared.config import POSTGRES_USER, POSTGRES_PASSWORD, DB_HOST, POSTGRES_DB, DB_PORT

# Замените следующие значения настройками вашей базы данных
DATABASE_URI = f'postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DB_HOST}:{DB_PORT}/{POSTGRES_DB}'
# print(f"{DATABASE_URI=}")
# Асинхронный движок и сессия
engine = create_async_engine(DATABASE_URI)
async_session = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Синхронный движок и сессия для Alembic
sync_DATABASE_URI = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DB_HOST}:{DB_PORT}/{POSTGRES_DB}'
sync_engine = create_engine(sync_DATABASE_URI)
sync_session = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)


class BaseModel:

    @classmethod
    def model_lookup_by_table_name(cls, table_name):
        registry_instance = getattr(cls, "registry")
        for mapper_ in registry_instance.mappers:
            model = mapper_.class_
            if not hasattr(model, "__tablename__"):
                model_class_name = model.__table__.name
            else:
                model_class_name = model.__tablename__
            if model_class_name == table_name:
                return model


Base = declarative_base(cls=BaseModel)

# Base = declarative_base()
