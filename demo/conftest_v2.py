import logging

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session
from sqlalchemy.sql import text
from shared import config
from shared.database import sync_DATABASE_URI
from shared.models import Base, User
from sqlalchemy.orm.session import Session
from sqlalchemy_utils import database_exists, create_database, drop_database

# pytest digest_service/tests/testsconf.py -v -o log_cli=true
logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


@pytest.fixture(scope="session")
def connection():
    db_url = f'postgresql://{config.POSTGRES_USER}:{config.POSTGRES_PASSWORD}@{config.DB_HOST}:{config.DB_PORT}/{config.POSTGRES_TEST_DB}'
    engine = create_engine(db_url)
    if not database_exists(engine.url):
        create_database(engine.url)

    yield engine.connect()
    # if not database_exists(engine.url):
    #     drop_database(engine.url)


@pytest.fixture(scope="session")
def setup_database(connection):
    # Base.metadata.bind = connection
    Base.metadata.create_all(bind=connection)
    yield
    Base.metadata.drop_all(bind=connection)


@pytest.fixture
def db_session(setup_database, connection):
    # transaction = connection.begin()
    yield scoped_session(
        sessionmaker(autocommit=False, autoflush=False, bind=connection)
    )

    # transaction.rollback()


@pytest.fixture()
def create_user(db_session: Session):
    users = [
        {
            "user_id": 1,
            "username": "Ivan",
        },
        # ...
    ]

    for user in users:
        db_user = User(**user)
        db_session.add(db_user)
    db_session.commit()


def test_user(db_session: Session, create_user):
    user = db_session.query(User).first()
    assert user.username == "Ivan"
