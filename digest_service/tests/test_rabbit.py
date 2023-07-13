import pytest
import asyncio
from shared.rabbitmq import Producer, Subscriber, MessageData, QueuesType
from digest_service.digest_main import prepare_digest


def add_args(func):
    def wrapper(*args, **kwargs):
        wrapper.args = args
        return func(*args, **kwargs)

    return wrapper


@pytest.mark.skip
@pytest.mark.asyncio
async def test_simple_send_receive_message(event_loop):
    @add_args
    def on_message(data):
        print(f"{data=}")

    producer = Producer(host="localhost", queue=QueuesType.ping)
    message: MessageData = {
        "type": "test_message",
        "data": "test_data"
    }
    await producer.send_message(message_with_data=message, queue=QueuesType.ping)
    subscriber = Subscriber(host="localhost", queue=QueuesType.ping)
    subscriber.subscribe("test_message", on_message)
    await subscriber.get_all_messages()
    assert "test_data" in on_message.args


@pytest.mark.asyncio
async def test_messages_prepare_digest(event_loop, session, load_data_from_json):
    @add_args
    def on_message_send_digest(data):
        print(f"{data=}")

    @add_args
    def on_message_no_digest(data):
        print(f"{data=}")

    load_data_from_json("data_set02.json")
    subscriber = Subscriber(host="localhost", queue=QueuesType.bot_service)
    await prepare_digest({"user_id": 2})
    await prepare_digest({"user_id": 1})

    subscriber.subscribe("send_digest", on_message_send_digest)
    subscriber.subscribe("no_digest", on_message_no_digest)

    await subscriber.get_all_messages()
    assert {
               "user_id": 2,
               "digest_id": 4,
           } in on_message_send_digest.args
    assert {
               "user_id": 1
           } in on_message_no_digest.args
