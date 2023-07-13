import asyncio
from shared.rabbitmq import Subscriber, Producer, QueuesType, MessageData
from shared.config import RABBIT_HOST


async def on_message(message_data):
    print(f"Receive message with data = {message_data}")
    await asyncio.sleep(5)
    producer = Producer(host=RABBIT_HOST, queue=QueuesType.ping)

    message: MessageData = {
        "type": "pong",
        "data": "pong_data"
    }
    await producer.send_message(message_with_data=message, queue=QueuesType.ping)


async def main():
    subscriber = Subscriber(host=RABBIT_HOST, queue=QueuesType.pong)
    subscriber.subscribe(message_type="ping", callback=on_message)
    await subscriber.run()
    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
