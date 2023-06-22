import asyncio
from shared.rabbitmq import Subscriber, QueuesType
from shared.config import RABBIT_HOST


async def update_digest():
    pass


async def prepare_digest():
    pass


async def main():
    subscriber = Subscriber(host=RABBIT_HOST, queue=QueuesType.pong)
    # subscriber.subscribe(message_type="ping", callback=on_message)
    # await subscriber.run()
    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
