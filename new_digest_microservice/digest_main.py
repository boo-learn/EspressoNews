import datetime

import redis
import schedule
import time
import json
import logging
from shared.models import Post


def fetch_and_clear_posts_atomic():
    # Создание пула соединений
    pool = redis.ConnectionPool(host='redis', port=6379, db=0)
    r = redis.Redis(connection_pool=pool)

    # Использование пайплайна для атомарных операций
    with r.pipeline() as pipe:
        pipe.multi()
        pipe.lrange('posts', 0, -1)
        pipe.delete('posts')
        results = pipe.execute()

    posts_json = results[0]
    posts = [json.loads(post.decode('utf-8')) for post in posts_json]

    return [Post(**post) for post in posts]


def run():
    logging.info(f"Проверяем посты")
    posts = fetch_and_clear_posts_atomic()

    # Вывести полученные посты в лог
    for post in posts:
        logging.info(f"Получен пост: {post.title}")


def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    while datetime.datetime.now().second != 0:
        time.sleep(1)

    # Настроим расписание для запуска функции каждую минуту
    schedule.every().minute.do(run)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    main()
