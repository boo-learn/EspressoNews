import asyncio
import datetime

import redis
import schedule
import time
import json
import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from summary import update_post_and_generate_summary_async
from shared.db_utils import get_user_settings
from sqlalchemy import select, and_

from shared.models import Post, User, Subscription, Digest, Role, Intonation, Summary
from shared.database import async_session
from shared.loggers import get_logger
from dateutil.parser import parse


logger = get_logger('digest.main')


def fetch_and_clear_posts_atomic(r: redis.Redis):
    # Использование пайплайна для атомарных операций
    with r.pipeline() as pipe:
        pipe.multi()
        pipe.lrange('posts', 0, -1)
        pipe.delete('posts')
        results = pipe.execute()

    posts_json = results[0]
    posts = [json.loads(post.decode('utf-8')) for post in posts_json]

    for post in posts:
        post["post_date"] = parse(post["post_date"])

    return [Post(**post) for post in posts]


async def run(r: redis.Redis):
    posts = fetch_and_clear_posts_atomic(r)
    logger.info(f"Получено {len(posts)} постов")

    if len(posts) > 0:
        async with async_session() as session:
            try:
                tasks = []
                i = 0
                session.add_all(posts)
                await session.commit()
            except IntegrityError as e:
                logger.error(f"Integrity error", error=e)
                await session.rollback()
                return  # это прервет дальнейшее выполнение функции после обработки ошибки
            logger.info("Посты добавлены в сессию")

            for post in posts:
                unique_combinations = set()
                post_logger = logger.bind(title=post.title, channel=post.channel_id)
                post_logger.info(f"Начинаем обработку поста")
                result = await session.execute(
                    select(User).join(Subscription).filter(Subscription.channel_id == post.channel_id).options(
                        joinedload(User.settings))
                )
                users = result.scalars().all()
                post_logger.info(f"{len(users)} пользователей подписаны на канал")

                for user in users:
                    user_logger = post_logger.bind(user_id=user.user_id)
                    user_logger.info(f"Начинаем обработку пользователя")

                    digest_result = await session.execute(
                        select(Digest).filter(
                            Digest.user_id == user.user_id,
                            Digest.is_active == True
                        ).options(
                            joinedload(Digest.digest_recs)
                        )
                    )

                    digest = digest_result.unique().scalar_one_or_none()

                    if digest.role_id != user.settings.role_id or digest.intonation_id != user.settings.intonation_id:
                        user_logger.info(f"Роль/интонация пользователя отличается от роли/интонации дайджеста")
                        digest.role_id = user.settings.role_id
                        digest.intonation_id = user.settings.intonation_id
                        digest.digest_ids.clear()
                        await session.commit()
                    user_logger.info(f"Добавляем пост к дайджесту")
                    digest.digest_ids.append(post.id)
                    combination = (digest.role_id, digest.intonation_id)
                    if combination in unique_combinations:
                        user_logger.info(f"Комбинация уже обработана", combination=combination)
                        continue

                    unique_combinations.add(combination)
                    user_logger.info(f"Добавили новую комбинацию", combination=combination)

                    role_result = await session.execute(select(Role).filter(Role.id == digest.role_id))
                    role_obj = role_result.scalars().first()
                    intonation_result = await session.execute(
                        select(Intonation).filter(Intonation.id == digest.intonation_id))
                    intonation_obj = intonation_result.scalars().first()

                    tasks.append(update_post_and_generate_summary_async(session, i, post, role_obj, intonation_obj))
                    user_logger.info(f"Добавлена задача", task_num=i)
                    i += 1

                post_logger.info(f"Завершена обработка поста")

            logger.info(f"Начинаем выполнение {i} задач")
            results = await asyncio.gather(*tasks)
            logger.info(f"Задачи выполнены, получено {len(results)} результатов")

            await session.commit()
            logger.info("Транзакция подтверждена")


async def main():
    # Создание пула соединений
    pool = redis.ConnectionPool(host='redis', port=6379, db=0)
    r = redis.Redis(connection_pool=pool)

    # logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
    #                     datefmt='%Y-%m-%d %H:%M:%S')

    while True:
        await run(r)
        await asyncio.sleep(1)


if __name__ == '__main__':
    asyncio.run(main())
