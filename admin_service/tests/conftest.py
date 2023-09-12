import os
import asyncio
import pytest
from pathlib import Path
import time
from loguru import logger
import socket
from uuid import uuid4
from docker import APIClient
from docker.errors import ImageNotFound
from fastapi.testclient import TestClient
from typing import Generator
from admin_service.main import app
from admin_service.models.admin_user import AdminUser

pytest_plugins = ['db_fixtures', 'auth_fixtures']

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

    def wrapper() -> str:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(('localhost', 0))
            return sock.getsockname()[1]
            # return "5430"

    return wrapper


@pytest.fixture(scope='session')
def db_server(unused_port, session_uuid: str):
    """
    Create docker-container with TestDB
    """
    client = APIClient()

    while True:
        try:
            # port = unused_port()
            port = "5430"
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
                healthcheck={'test': ['CMD', 'pg_isready', '-U', 'postgres'], 'interval': 10_000_000},
            )
            container["db_port"] = port
            break
        except ImageNotFound:
            client.pull("postgres")

    client.start(container=container['Id'])
    try:
        while get_health(container) != 'healthy':
            print("~~~~~~~~~~~~~~~~~~~~", get_health(container))
            time.sleep(0.1)
        time.sleep(0.5)
        yield container
    except Exception as e:
        raise e
    finally:
        client.kill(container=container['Id'])
        client.remove_container(container['Id'])


# @pytest.fixture(scope='session', autouse=True)
@pytest.fixture(scope='session')
def rabbitmq_server(unused_port, session_uuid: str):
    """
    Create docker-container with TestRabbitMQ
    """
    client = APIClient()

    while True:
        try:
            port = unused_port()
            container = client.create_container(
                "rabbitmq",
                name=f"test-rabbitmq-{session_uuid}",
                hostname="localhost",
                ports=[5672],
                detach=True,
                host_config=client.create_host_config(
                    port_bindings={5672: port}  # {in: out}
                ),
                healthcheck={'test': ["CMD", "rabbitmqctl", "status"],
                             'interval': 1_000_000_000,
                             'timeout': 5_000_000_000,
                             'retries': 4,
                             }
            )
            container["rabbit_port"] = port
            break
        except ImageNotFound:
            print("Download Rabbit Image")
            client.pull("rabbitmq")

    client.start(container=container['Id'])
    try:
        while get_health(container) != 'healthy':
            print("~~~~~~~~~~~~~~~~~~~~", get_health(container))
            time.sleep(1)
        print("~~~~~~~~~~~~~~~~~~~~", get_health(container))
        time.sleep(1)
        yield container
    except Exception as e:
        raise e
    finally:
        client.kill(container=container['Id'])
        client.remove_container(container['Id'])


@pytest.fixture(scope='session')
def path():
    return Path(__file__).parent


@pytest.fixture(scope='session')
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
#  -> Generator
def client(session):
    with TestClient(app) as test_client:
        yield test_client
