import logging

import pytest
from pytest_postgresql import factories
from pytest_postgresql.janitor import DatabaseJanitor
from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker
from shared import config

# pytest digest_service/tests/testsconf.py -v -o log_cli=true
from shared.models import Base

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

test_db = factories.postgresql_noproc(
    host=config.DB_HOST.split(":")[0],
    port=5432,
    user=config.POSTGRES_USER,
    password=config.POSTGRES_PASSWORD,
    dbname=config.POSTGRES_TEST_DB
)


@pytest.fixture(scope="session")
def db_session(test_db):
    # print("!" * 100)
    """Session for SQLAlchemy."""
    pg_host = test_db.host
    pg_port = test_db.port
    pg_user = test_db.user
    pg_password = test_db.password
    pg_db = test_db.dbname

    with DatabaseJanitor(
            pg_user, pg_host, pg_port, pg_db, test_db.version, pg_password
    ):
        connection_str = f"postgresql+psycopg2://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}"
        engine = create_engine(connection_str)
        with engine.connect() as con:
            Base.metadata.create_all(con)
            con.commit()
            logger.info("yielding a sessionmaker against the test postgres db.")

            yield sessionmaker(bind=engine, expire_on_commit=False)
