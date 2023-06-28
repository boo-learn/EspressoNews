import logging

import pytest

pytest_plugins = ['db_fixtures']
logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
