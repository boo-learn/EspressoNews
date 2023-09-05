from loguru import logger
import pytest
from typing import Generator
from sqlalchemy import create_engine, select, func, insert, Table, inspect
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from shared.models import Base
from sqlalchemy.sql import text as sa_text
from sqlalchemy.pool import NullPool
import json
from shared.database import sync_DATABASE_URI
from shared.database import Base as BaseModel


@pytest.fixture(scope='session')
def engine(db_server):
    # port = db_server["db_port"]
    engine: Engine = create_engine(sync_DATABASE_URI, future=True, poolclass=NullPool)
    # logger.info(f"{sync_DATABASE_URI=}")
    yield engine


@pytest.fixture(scope='function')
#  -> Generator[Session]
def session(engine: Engine):
    session_maker = sessionmaker(bind=engine)
    with session_maker() as session:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        yield session

    # print("session end")


@pytest.fixture(scope="function")
def create_objects(session):
    def _create_objects(object_type: type[BaseModel], objects_data: list[dict]) -> list[BaseModel]:
        objects = []
        for object_data in objects_data:
            obj = object_type(**object_data)
            objects.append(obj)
            session.add(obj)
        session.commit()
        return objects

    return _create_objects


@pytest.fixture(scope="function")
def create_object(session):
    def _create_object(object_type: type[BaseModel], object_data: dict) -> BaseModel:
        obj = object_type(**object_data)
        session.add(obj)
        session.commit()
        return obj

    return _create_object



# @pytest.fixture(scope="function")
# def load_data_from_json(path, session):
#     def _load_data_from_json(json_name):
#         file_name = path / "data" / json_name
#         with open(file_name, "r", encoding="UTF-8") as f:
#             data = json.load(f)
#             inspector = inspect(session.bind)
#             for table_name, values in data.items():
#                 model = Base.model_lookup_by_table_name(table_name)
#                 for value in values:
#                     obj = model(**value)
#                     session.add(obj)
#                     session.commit()
#                 for column in inspector.get_columns(table_name):
#                     if column['autoincrement']:
#                         session.execute(sa_text(
#                             f"SELECT setval('{table_name}_{column['name']}_seq', "
#                             f"(SELECT MAX({column['name']}) FROM {table_name}))")
#                         )
#                         session.commit()
#                 # if table_name == 'digests':
#                 #     session.execute(sa_text("ALTER SEQUENCE digests_id_seq RESTART WITH 10"))
#             # session.commit()
#
#     return _load_data_from_json
