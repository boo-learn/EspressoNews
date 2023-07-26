import logging
import asyncio
from sqlalchemy import select, inspect
from shared.rabbitmq import Subscriber, QueuesType, MessageData, Producer
from shared.config import RABBIT_HOST
from shared.database import async_session
from shared.models import User, Digest, Post, digests_posts, Subscription
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_digest(user_id: int) -> Optional[Digest]:
    logger.info(f"Start digest creating.")
    digest = Digest(user_id=user_id)
    async with async_session() as session:
        already_in_digests = select(digests_posts.c.post_id).join(Digest).where(Digest.user_id == user_id)
        stmt = (select(Post)
                .join(Subscription, Post.channel_id == Subscription.channel_id)
                .join(User, Subscription.user_id == User.user_id)
                .where(User.user_id == user_id,
                       ~Post.post_id.in_(already_in_digests))
                )
        results = await session.execute(stmt)
        new_posts_for_user = results.scalars().all()
        if not new_posts_for_user:
            return None
        posts_without_duplicates = await exclude_duplicates(new_posts_for_user)
        session.add(digest)
        digest.digest_ids.extend([post.post_id for post in posts_without_duplicates])
        await session.commit()
        return digest


async def prepare_digest(data: int):
    logger.info(f"Start digest prepare.")
    logger.info(f"{data}")
    user_id = data
    digest = await create_digest(user_id)

    if digest:
        producer = Producer(host=RABBIT_HOST, queue=QueuesType.summary_service)
        logger.info(f"digest")
        message: MessageData = {
            "type": "summarize_digest",  # send_digest
            "data": {
                "user_id": digest.user_id,
                "digest_id": digest.id,
            }
        }
        print(f"{message=}")
        await producer.send_message(message_with_data=message, queue=QueuesType.summary_service)
    else:
        producer = Producer(host=RABBIT_HOST, queue=QueuesType.bot_service)
        logger.info(f"no digest")
        message: MessageData = {
            "type": "no_digest",
            "data": {
                "user_id": user_id
            }
        }
        print(f"{message=}")
        await producer.send_message(message_with_data=message, queue=QueuesType.bot_service)
    logger.info(f"End digest prepare.")


async def exclude_duplicates(posts: list[Post]) -> list[Post]:
    ...
    return posts


async def main():
    logger.info(f"Start digest service.")
    # example message "prepare_digest"
    message: MessageData = {
        "type": "prepare_digest",
        "data": {"user_id": 1}
    }
    subscriber = Subscriber(host=RABBIT_HOST, queue=QueuesType.digest_service)
    subscriber.subscribe(message_type="prepare_digest", callback=prepare_digest)
    await subscriber.run()
    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
