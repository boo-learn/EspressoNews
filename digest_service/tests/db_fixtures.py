import pytest
from sqlalchemy import create_engine, select, func, insert, Table
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from shared.models import Base, User
from sqlalchemy.sql import text as sa_text
import json


@pytest.fixture(scope='session')
def engine(db_server):
    port = db_server["db_port"]
    engine: Engine = create_engine(f'postgresql://postgres:postgres@localhost:{port}/TestDB', future=True)
    yield engine


@pytest.fixture(scope='function')
def session(engine: Engine):
    print("Session start")
    session_maker = sessionmaker(bind=engine)
    with session_maker() as session:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        yield session

    # print("session end")


@pytest.fixture(scope="function")
def create_object(session):
    def _create_object(object_type, object_data):
        obj = object_type(**object_data)
        session.add(obj)
        session.commit()
        return obj

    return _create_object


@pytest.fixture(scope="function")
def load_data_from_json(path, session):
    def _load_data_from_json(json_name):
        file_name = path / "data" / json_name
        with open(file_name, "r", encoding="UTF-8") as f:
            data = json.load(f)
            for table_name, values in data.items():
                model = Base.model_lookup_by_table_name(table_name)
                for value in values:
                    obj = model(**value)
                    session.add(obj)
                    session.commit()
                # if table_name == 'digests':
                #     session.execute(sa_text("ALTER SEQUENCE digests_id_seq RESTART WITH 10"))
            # session.commit()

    return _load_data_from_json
