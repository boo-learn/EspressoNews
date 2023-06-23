import asyncio
from shared.rabbitmq import Subscriber, QueuesType
from shared.config import RABBIT_HOST
from shared.database import async_session
from shared.models import User


async def create_user():
    session = async_session()
    user = User(username="test_user")
    session.add(user)
    session.commit()


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
