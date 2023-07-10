import asyncio
from sqlalchemy import select, inspect
from shared.rabbitmq import Subscriber, QueuesType, MessageData, Producer
from shared.config import RABBIT_HOST
from shared.database import async_session
from shared.models import User, Digest, Post, digests_posts, Subscription


# async def update_digest():
#     pass
async def create_digest(user_id: int):
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
        posts_without_duplicates = await exclude_duplicates(new_posts_for_user)
        session.add(digest)
        digest.digest_ids.extend([post.post_id for post in posts_without_duplicates])
        collect_summary = ""
        for post in posts_without_duplicates:
            collect_summary += f"• {post.summary}\n\n"
        digest.total_summary = collect_summary
        await session.commit()
        # session.expunge(digest)
        return digest.id


async def prepare_digest(user_id: int):
    producer = Producer(host=RABBIT_HOST)
    digest_id = await create_digest(user_id)

    message: MessageData = {
        "type": "send_digest",
        "data": digest_id
    }
    await producer.send_message(message_with_data=message, queue=QueuesType.bot_service)


async def exclude_duplicates(posts: list[Post]) -> list[Post]:
    ...
    return posts


async def main():
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
