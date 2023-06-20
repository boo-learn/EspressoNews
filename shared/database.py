from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import POSTGRES_USER, POSTGRES_PASSWORD, DB_HOST, POSTGRES_DB

# Замените следующие значения настройками вашей базы данных
DATABASE_URI = f'postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DB_HOST}/{POSTGRES_DB}'

# Асинхронный движок и сессия
engine = create_async_engine(DATABASE_URI)
async_session = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Синхронный движок и сессия для Alembic
sync_DATABASE_URI = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DB_HOST}/{POSTGRES_DB}'
sync_engine = create_engine(sync_DATABASE_URI)
sync_session = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

Base = declarative_base()
