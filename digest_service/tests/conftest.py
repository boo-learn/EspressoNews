import asyncio
import pytest
from pathlib import Path
import time
import logging
import socket
from uuid import uuid4
from docker import APIClient
from docker.errors import ImageNotFound

pytest_plugins = ['db_fixtures']


logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


@pytest.fixture(scope='session')
def session_uuid() -> str:
    """Return a unique uuid string to provide label to identify the image build for this session"""
    return str(uuid4())


def get_health(container):
    api_client = APIClient()
    inspect_results = api_client.inspect_container(container["Id"])
    # print(inspect_results)
    # print(inspect_results['State'])
    # print(inspect_results['State']['Health'])
    # print(inspect_results['State']['Health']['Status'])
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


@pytest.fixture(scope='session', autouse=True)
def rabbitmq_server(unused_port, session_uuid: str):
    """
    Create docker-container with TestRabbitMQ
    """
    client = APIClient()

    while True:
        try:
            port = "5672"
            container = client.create_container(
                "rabbitmq:3-management",
                name=f"test-rabbitmq-{session_uuid}",
                hostname="localhost",
                ports=[port, 15672],
                detach=True,
                host_config=client.create_host_config(
                    port_bindings={port: 5672, 15672: 15672}
                ),
                healthcheck={'test': ["CMD", "rabbitmqctl", "status"],
                             'interval': 15000000000,
                             'timeout': 5000000000,
                             'retries': 2,
                             }
            )
            container["rabbit_port"] = port
            break
        except ImageNotFound:
            client.pull("rabbitmq:3-management")

    client.start(container=container['Id'])
    while True:
        print("~~~~~~~~~~~~~~~~~~~~", get_health(container), '\n\n\n\n')
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


@pytest.fixture(scope='session')
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()