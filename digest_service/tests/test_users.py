import pytest
# from .testsconf import db_session, logger, test_db
from shared.models import User


@pytest.fixture(scope="module")
def create_test_data():
    """Let's create the test data with the three witches names."""
    names = ["Winifred", "Sarah", "Mary"]
    test_objs = []
    for name in names:
        test_objs.append(User(username=name, language_code="ru"))

    return test_objs


def test_create_user(db_session, create_test_data):
    s = db_session()
    for obj in create_test_data:
        s.add(obj)
    s.commit()
    logger.info("Added test data to the database.")

    query_result = s.query(User).all()
    print(f"{query_result}")
    s.close()

    assert create_test_data[0].username in query_result[0].username
