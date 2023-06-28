import asyncio
from shared.rabbitmq import Producer, Subscriber, QueuesType, MessageData
from shared.config import RABBIT_HOST


async def on_message(message_data):
    print(f"Receive message with data = {message_data}")
    await asyncio.sleep(3)
    producer = Producer(host=RABBIT_HOST)
    message: MessageData = {
        "type": "ping",
        "data": "ping_data"
    }
    await producer.send_message(message_with_data=message, queue=QueuesType.pong)


async def main():
    message: MessageData = {
        "type": "ping",
        "data": "ping_data"
    }
    producer = Producer(host=RABBIT_HOST)
    await producer.send_message(message_with_data=message, queue=QueuesType.pong)

    subscriber = Subscriber(host=RABBIT_HOST, queue=QueuesType.ping)
    subscriber.subscribe(message_type="pong", callback=on_message)
    await subscriber.run()
    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
