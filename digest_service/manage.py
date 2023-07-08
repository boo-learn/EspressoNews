# Чтобы запускать скрипт локально, находясь в корневой директории проекта
import sys, os

sys.path.append(os.getcwd())
import click
from shared.models import User, Channel, Subscription, Post, Digest
from shared.database import sync_session, sync_engine
from shared.models import Base
from contextlib import contextmanager
import contextlib
from sqlalchemy import select, insert, Table
from sqlalchemy.sql import text as sa_text
import json
from pprint import pprint
from pathlib import Path

BASE_DIR = Path(__file__).parent


@click.group()
def cli():
    pass


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = sync_session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def create_object(session, object_type: Base, object_data: dict):
    obj = object_type(**object_data)
    session.add(obj)
    session.commit()
    print(obj.user_id)
    return obj


def delete_objects(session, object_type: Base):
    session.query(object_type).delete()
    session.commit()


@cli.command()
def create_user():
    user_data = {
        "username": "user4"
    }
    with session_scope() as session:
        create_object(session, User, user_data)


@cli.command()
def load_data():
    subscribe = Subscription(
        user=User(user_id=1, username="user-1"),
        channel=Channel(
            channel_id=1,
            channel_name="Channel-1",
            channel_username="Author Channel-1",
            posts=[
                Post(post_id=1, title="Post-1 from Channel-1", content="Content for Post-1"),
                Post(post_id=2, title="Post-2 from Channel-1", content="Content for Post-2"),
                Post(post_id=3, title="Post-3 from Channel-1", content="Content for Post-3"),
            ], )
    )

    with session_scope() as session:
        session.add(subscribe)

    user2 = User(user_id=2, username="user-2")
    user3 = User(user_id=3, username="user-3")
    channel2 = Channel(
        channel_id=2,
        channel_name="Channel-2",
        channel_username="Author Channel-2",
        posts=[
            Post(post_id=5, title="Post-21 from Channel-2", content="Content for Post-21"),
            Post(post_id=6, title="Post-22 from Channel-2", content="Content for Post-22"),
            Post(post_id=7, title="Post-23 from Channel-2", content="Content for Post-23"),
            Post(post_id=8, title="Post-24 from Channel-2", content="Content for Post-24"),
        ], )

    channel3 = Channel(
        channel_id=3,
        channel_name="Channel-3",
        channel_username="Author Channel-3",
        posts=[
            Post(post_id=9, title="Post-31 from Channel-3", content="Content for Post-31"),
            Post(post_id=10, title="Post-32 from Channel-3", content="Content for Post-32"),
        ], )
    digest = Digest(id=1, user_id=3, posts=[])

    subscribe2 = Subscription(user_id=2, channel_id=2)
    subscribe3 = Subscription(user_id=3, channel_id=2)
    subscribe4 = Subscription(user_id=3, channel_id=3)
    with session_scope() as session:
        session.add_all([user2, user3])
        session.commit()
        session.add_all([channel2, channel3])
        session.commit()
        session.add_all([subscribe2, subscribe3, subscribe4])
        session.commit()
        session.add(digest)
        session.commit()
        digest.digest_ids.extend([9, 10])
        session.commit()
        # digest.posts


@cli.command()
def clear_db():
    with contextlib.closing(sync_engine.connect()) as con:
        trans = con.begin()
        for table in reversed(Base.metadata.sorted_tables):
            con.execute(sa_text(f'TRUNCATE TABLE {table} CASCADE;'))
        trans.commit()


@cli.command()
def delete_users():
    with session_scope() as session:
        delete_objects(session, User)


@cli.command()
def dump_db(file_name=BASE_DIR / "data" / "data.json"):
    with session_scope() as session:
        result = {}
        for table in Base.metadata.sorted_tables:
            # if models_only and table.name not in [model.__tablename__ for model in models_only]:
            #     continue
            result[table.name] = list(map(dict, session.execute(table.select()).mappings().all()))

        with open(file_name, "w", encoding="UTF-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2, default=str)


@cli.command()
def load_db(file_name=BASE_DIR / "data" / "data_set01.json"):
    with open(file_name, "r", encoding="UTF-8") as f:
        data = json.load(f)
        with session_scope() as session:
            for table_name, values in data.items():
                table = Table(table_name, Base.metadata,
                              autoload_replace=False,
                              keep_existing=False,
                              )
                query_insert = insert(table)
                # print(values)
                # session.execute(table.insert(), values)
            # session.commit()
                for value in values:
                    print(f"{value=}")
                    query_insert = query_insert.values(value)
                    session.execute(query_insert)
                # session.commit()


if __name__ == '__main__':
    cli()

# NOTES

# Get all posts for user:
# q_posts = select(Post).join(Subscription, Post.channel_id==Subscription.channel_id)\
#     .join(User, Subscription.user_id==User.user_id).where(User.user_id==user_id)
# posts = session.scalars(q_posts)

# Fined by ids
# posts = session.scalars(select(Post).where(Post.post_id.in_([9, 10]))).all()


# already_in_digests =select(digests_posts.c.post_id).join(Digest).where(Digest.user_id==user_id)
# posts = session.scalars(select(Post.post_id)
#                         .join(Subscription, Post.channel_id==Subscription.channel_id)
#                         .join(User, Subscription.user_id==User.user_id)
#                         .where(User.user_id==user_id, ~Post.post_id.in_(already_in_digests))).all()
