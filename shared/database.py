from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import POSTGRES_USER, POSTGRES_PASSWORD, DB_HOST, POSTGRES_DB

# Замените следующие значения настройками вашей базы данных
DATABASE_URI = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DB_HOST}/{POSTGRES_DB}'

engine = create_engine(DATABASE_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
