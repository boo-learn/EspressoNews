import pytest
from digest_service.tests.conftest import logger


@pytest.fixture
def string():
    return 'hello'


def test_a():
    assert 1 != 2


class TestB:
    def test_b(self, string):
        assert string.lower() != string.upper()

    def test_c(self):
        with pytest.raises(ZeroDivisionError):
            1 / 0


# fixture scopes
# @pytest.fixture(scope="session")
# @pytest.fixture(scope="module")
# @pytest.fixture(scope="class")
# @pytest.fixture(scope="function")


# fixture factory
@pytest.fixture
def make_rnd_string():
    import random

    def maker():
        return random.choice(["hello", "hi", "by"])

    return maker


def test_string(make_rnd_string):
    s1 = make_rnd_string()
    s2 = make_rnd_string()
    assert s1 != s2


# tear_down factory

@pytest.fixture
def open_file():
    f = None

    def opener(filename):
        nonlocal f
        logger.info(f"{f}")
        # assert f is None
        f = open(filename)
        return f

    yield opener
    if f is not None:
        f.close()


def test_file(open_file):
    assert open_file("file1.txt").read() == "data1"
    assert open_file("file2.txt").read() == "data2"
