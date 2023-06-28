import pytest
from sqlalchemy import create_engine, select, func
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from shared.models import Base, User


@pytest.fixture(scope='module')
def engine():
    engine: Engine = create_engine('postgresql://postgres:postgres@localhost:5432/TestDB', future=True)
    yield engine


@pytest.fixture(scope='module')
def session(engine: Engine):
    session_maker = sessionmaker(bind=engine, future=True)
    with session_maker() as session:
        Base.metadata.create_all(bind=engine)
        yield session
    # session.rollback()


@pytest.fixture(scope="module")
def create_user(session):
    def _create_user(user_data):
        user = User(**user_data)
        session.add(user)
        session.commit()
        return user

    return _create_user


def test_create_user(session, create_user):
    # session = db_session()
    user = create_user({"username": "Ivan"})
    # logger.info("Added user to the database.")

    query_result = session.query(User).first()
    # session.close()

    assert user.username == query_result.username