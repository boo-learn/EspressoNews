from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import POSTGRES_USER, POSTGRES_PASSWORD, DB_HOST, POSTGRES_DB

# Замените следующие значения настройками вашей базы данных
DATABASE_URI = f'postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DB_HOST}/{POSTGRES_DB}'

engine = create_async_engine(DATABASE_URI)
async_session = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
