import pytest
from pathlib import Path
import time
import logging
import socket
from uuid import uuid4
from docker import APIClient
from docker.errors import ImageNotFound

pytest_plugins = ['db_fixtures']


# logging.basicConfig()
# logger = logging.getLogger()
# logger.setLevel(logging.DEBUG)


@pytest.fixture(scope='session')
def session_uuid() -> str:
    """Return a unique uuid string to provide label to identify the image build for this session"""
    return str(uuid4())


def get_health(container):
    api_client = APIClient()
    inspect_results = api_client.inspect_container(container["Id"])
    return inspect_results['State']['Health']['Status']


@pytest.fixture(scope="session")
def unused_port():
    """
    Find unused port
    """

    def wrapper():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(('localhost', 0))
            # return sock.getsockname()[1]
            return "5430"

    return wrapper


@pytest.fixture(scope='session', autouse=True)
def db_server(unused_port, session_uuid: str):
    """
    Create docker-container with TestDB
    """
    client = APIClient()

    while True:
        try:
            port = unused_port()
            container = client.create_container(
                "postgres",
                name=f"test-postgres-{session_uuid}",
                ports=[5432],
                detach=True,
                host_config=client.create_host_config(
                    port_bindings={5432: port}
                ),
                environment={
                    "POSTGRES_USER": "postgres",
                    "POSTGRES_PASSWORD": "postgres",
                    "POSTGRES_DB": "TestDB"
                },
                healthcheck={'test': ['CMD', 'pg_isready', '-U', 'postgres'], 'interval': 100000000},
            )
            container["db_port"] = port
            break
        except ImageNotFound:
            client.pull("postgres")

    client.start(container=container['Id'])
    while True:
        print("~~~~~~~~~~~~~~~~~~~~", get_health(container))
        time.sleep(0.5)
        if get_health(container) == 'healthy':
            print("~~~~~~~~~~~~~~~~~~~~", get_health(container))
            time.sleep(1)
            break

    yield container
    client.kill(container=container['Id'])
    client.remove_container(container['Id'])


@pytest.fixture(scope='session')
def path():
    return Path(__file__).parent
