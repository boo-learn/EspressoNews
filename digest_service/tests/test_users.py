import pytest
from shared.models import User
from conftest import logger


# @pytest.fixture(scope="module", params=["Winifred", "Sarah", "Mary"])
# def create_test_data(request):
#     return User(username=request.param, language_code="ru")

@pytest.fixture(scope="module")
def create_user(db_session):
    def _create_user(user_data):
        user = User(**user_data)
        session = db_session()
        session.add(user)
        session.commit()
        return user

    return _create_user


def test_create_user(db_session, create_user):
    session = db_session()
    user = create_user({"username": "Ivan"})
    logger.info("Added user to the database.")

    query_result = session.query(User).first()
    session.close()

    assert user.username == query_result.username
