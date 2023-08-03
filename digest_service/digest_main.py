import asyncio
import logging
from typing import Optional

from sqlalchemy import select

from shared.config import RABBIT_HOST
from shared.database import async_session
from shared.db_utils import get_user_settings
from shared.models import User, Digest, Post, digests_posts, Subscription
from shared.rabbitmq import Subscriber, QueuesType, MessageData, Producer
from fuzzywuzzy import fuzz
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_digest(user_id: int) -> Optional[Digest]:
    logger.info(f"Start digest creating.")
    user_settings = await get_user_settings(user_id)
    digest = Digest(user_id=user_id, role_id=user_settings.role_id, intonation_id=user_settings.intonation_id)
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
        posts_without_duplicates = await asyncio.to_thread(exclude_duplicates, new_posts_for_user)
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


def exclude_duplicates(posts: list[Post]) -> list[Post]:
    # Get titles of the posts
    # titles = [post.title for post in posts]
    #
    # # Initialize an empty list to hold the posts without duplicates
    # posts_without_duplicates = []
    #
    # # For each post
    # for i in range(len(posts)):
    #     # Check if it's similar to any of the previously checked posts
    #     for j in range(i):
    #         # Calculate Levenshtein distance between the current post and the previous post
    #         similarity = fuzz.ratio(titles[i], titles[j])
    #
    #         # If the titles are similar
    #         if similarity > 60:
    #             # Break the inner loop and skip to the next post
    #             break
    #     else:
    #         # If the post is not similar to any previous post, add it to the list of posts without duplicates
    #         posts_without_duplicates.append(posts[i])
    #
    # return posts_without_duplicates
    pass


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
