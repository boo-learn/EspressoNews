from typing import (
    Any,
    Dict,
    List,
)
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker, DeclarativeBase

from shared.config import POSTGRES_USER, POSTGRES_PASSWORD, DB_HOST, POSTGRES_DB, DB_PORT

# Замените следующие значения настройками вашей базы данных
DATABASE_URI = f'postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DB_HOST}:{DB_PORT}/{POSTGRES_DB}'
print(f"{DATABASE_URI=}")
# Асинхронный движок и сессия
engine = create_async_engine(DATABASE_URI)
async_session = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)

# Синхронный движок и сессия для Alembic
sync_DATABASE_URI = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DB_HOST}:{DB_PORT}/{POSTGRES_DB}'
sync_engine = create_engine(sync_DATABASE_URI)
sync_session = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)


class Base(DeclarativeBase):
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

    @classmethod
    def schema(cls) -> str:
        """Return name of database schema the model refers to."""

        _schema = cls.__mapper__.selectable.schema
        if _schema is None:
            raise ValueError("Cannot identify model schema")
        return _schema

    @classmethod
    def table_name(cls) -> str:
        """Return name of the table the model refers to."""

        return cls.__tablename__

    @classmethod
    def fields(cls) -> List[str]:
        """Return list of model field names."""

        return cls.__mapper__.selectable.c.keys()

    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to a dictionary."""

        _dict: Dict[str, Any] = dict()
        for key in self.__mapper__.c.keys():
            _dict[key] = getattr(self, key)
        return _dict

