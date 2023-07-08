import pytest
from shared.models import User
from sqlalchemy import select
from conftest import logger


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
    user = create_user({"user_id": 1, "username": "Ivan"})
    # logger.info("Added user to the database.")

    query_result = session.scalar(select(User).where(User.user_id == 1))
    # query_result = session.scalars(select(User).where(User.user_id == 1)).one()
    # query_result = session.query(User).where(User.user_id==1)
    # session.close()

    assert user.username == query_result.username
