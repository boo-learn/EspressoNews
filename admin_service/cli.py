import sys, os
from loguru import logger

sys.path.append(os.getcwd())  # Чтобы запускать скрипт локально, находясь в корневой директории проекта
import click
import json
import asyncio
from pathlib import Path

import contextlib
from contextlib import contextmanager, asynccontextmanager
from functools import wraps

from sqlalchemy import select, insert, Table
from sqlalchemy import exc
from sqlalchemy.sql import text as sa_text

from shared.models import User, Channel, Subscription, Post, Digest
from shared.database import sync_session, sync_engine, async_session
from shared.models import Base

import schemas, repository

BASE_DIR = Path(__file__).parent


def coro(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper


@click.group()
def cli():
    pass


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = sync_session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


@asynccontextmanager
async def async_session_scope():
    """Provide a transactional scope around a series of operations."""
    session = async_session()
    try:
        yield session
        await session.commit()
    except:
        await session.rollback()
        raise
    finally:
        await session.close()


def delete_objects(session, object_type: Base):
    session.query(object_type).delete()
    session.commit()


@cli.command()
def clear_db():
    with contextlib.closing(sync_engine.connect()) as con:
        trans = con.begin()
        for table in reversed(Base.metadata.sorted_tables):
            con.execute(sa_text(f'TRUNCATE TABLE {table} CASCADE;'))
        trans.commit()




@cli.command()
@click.argument('filename')
def dump_db(filename="data.json"):
    full_path = BASE_DIR / "data" / filename
    with session_scope() as session:
        result = {}
        for table in Base.metadata.sorted_tables:
            # if models_only and table.name not in [model.__tablename__ for model in models_only]:
            #     continue
            result[table.name] = list(map(dict, session.execute(table.select()).mappings().all()))

        with open(full_path, "w", encoding="UTF-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2, default=str)


@cli.command()
@click.argument('filename')
def load_db(filename="data.json"):
    full_path = BASE_DIR / "data" / filename
    with open(full_path, "r", encoding="UTF-8") as f:
        data = json.load(f)
        with session_scope() as session:
            for table_name, values in data.items():
                model = Base.model_lookup_by_table_name(table_name)
                for value in values:
                    obj = model(**value)
                    session.add(obj)
                    session.commit()


@cli.command()
@click.option("--name", type=str, help="User name")
@click.option("--email", type=str, help="Email")
@click.option("--password", type=str, help="Password")
@coro
async def create_user(name: str, email: str, password: str) -> None:
    """Create new user.

    Write new user (with hashed password) to corresponding database table.

    \b
    Examples:
        myapi --name 'test user' --email test_user@myapi.com --password qwerty
    """

    # initialize user schema
    user = schemas.UserCreateSchema(name=name, email=email, password=password)

    async with async_session_scope() as session:
        try:
            await repository.admin_users.create(session, obj_data=user)
        except exc.IntegrityError:
            logger.info("SuperUser already created")
            await session.rollback()
        else:
            logger.info(f"New SuperUser created successfully")


if __name__ == '__main__':
    cli()
