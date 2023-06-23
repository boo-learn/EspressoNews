import pytest


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
