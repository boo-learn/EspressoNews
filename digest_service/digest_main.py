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
                       ~Post.post_id.in_(already_in_digests),
                       ~Post.summary.is_(None))
                )
        results = await session.execute(stmt)
        new_posts_for_user = results.scalars().all()
        if not new_posts_for_user:
            return None
        posts_without_duplicates = await exclude_duplicates(new_posts_for_user)
        session.add(digest)
        digest.digest_ids.extend([post.post_id for post in posts_without_duplicates])
        collect_summary = ""
        for post in posts_without_duplicates:
            collect_summary += f"• {post.summary}\n\n"
        digest.total_summary = collect_summary
        await session.commit()
        return digest


async def prepare_digest(user_id: int):
    producer = Producer(host=RABBIT_HOST)
    digest = await create_digest(user_id)

    if digest:
        message: MessageData = {
            "type": "send_digest",
            "data": {
                "user_id": digest.user_id,
                "digest_id": digest.id,
            }
        }
    else:
        message: MessageData = {
            "type": "no_digest",
            "data": {
                "user_id": user_id
            }
        }
    await producer.send_message(message_with_data=message, queue=QueuesType.bot_service)


async def exclude_duplicates(posts: list[Post]) -> list[Post]:
    ...
    return posts


async def main():
    logger.info(f"Start digest service.")
    # example message "prepare_digest"
    message: MessageData = {
        "type": "prepare_digest",
        "data": "[int]user_id"
    }
    subscriber = Subscriber(host=RABBIT_HOST, queue=QueuesType.digest_service)
    subscriber.subscribe(message_type="prepare_digest", callback=prepare_digest)
    await subscriber.run()
    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
