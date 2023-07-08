import pytest
import os
import asyncio
import pytest_asyncio
from shared.models import User, Channel, Post, Subscription, Digest
from sqlalchemy import select
from digest_service.digest_main import prepare_digest


# @pytest.fixture(scope='function')
# def load_data(session):
#     users = [
#         User(user_id=1, username="user-1"),
#         User(user_id=2, username="user-2"),
#         User(user_id=3, username="user-3")
#     ]
#     channels = [
#         Channel(
#             channel_id=1,
#             channel_name="Channel-1",
#             channel_username="Author Channel-1",
#             posts=[
#                 Post(post_id=1, title="Post-1 from Channel-1 with summary",
#                      content="Content for Post-1", summary="short content for post-1"),
#                 Post(post_id=2, title="Post-2 from Channel-1 without summary", content="Content for Post-2"),
#                 Post(post_id=3, title="Post-3 from Channel-1 with summary",
#                      content="Content for Post-3", summary="short content for post-3"),
#             ], ),
#         Channel(
#             channel_id=2,
#             channel_name="Channel-2",
#             channel_username="Author Channel-2",
#             posts=[
#                 Post(post_id=5, title="Post-21 from Channel-2 without summary", content="Content for Post-21"),
#                 Post(post_id=6, title="Post-22 from Channel-2 with summary",
#                      content="Content for Post-22", summary="short content for post-22"),
#                 Post(post_id=7, title="Post-23 from Channel-2 with summary",
#                      content="Content for Post-23", summary="short content for post-23"),
#                 Post(post_id=8, title="Post-24 from Channel-2 without summary", content="Content for Post-24"),
#             ], ),
#         Channel(
#             channel_id=3,
#             channel_name="Channel-3",
#             channel_username="Author Channel-3",
#             posts=[
#                 Post(post_id=9, title="Post-31 from Channel-3 with summary",
#                      content="Content for Post-31", summary="short content for post-31"),
#                 Post(post_id=10, title="Post-32 from Channel-3 with summary",
#                      content="Content for Post-32", summary="short content for post-32"),
#             ], )
#     ]
#     subscribes = [
#         Subscription(user_id=2, channel_id=2),
#         Subscription(user_id=3, channel_id=2),
#         Subscription(user_id=3, channel_id=3)
#     ]
#     session.add_all(users)
#     session.commit()
#     session.add_all(channels)
#     session.commit()
#     session.add_all(subscribes)
#     session.commit()


# @pytest.fixture(scope='function')
# def create_digest(session, load_data):
#     digest = Digest(user_id=3)
#     session.add(digest)
#     session.commit()
#     digest.digest_ids.extend([9, 10])
#     session.commit()

@pytest.mark.skip()
def test_create_digest(session, load_data_from_json):
    load_data_from_json("data_set01.json")
    digest = session.scalar(select(Digest))
    assert digest.user_id == 3
    assert digest.posts[0].post_id == 9
    assert digest.posts[1].post_id == 10


# @pytest.mark.skip()
@pytest.mark.asyncio
async def test_prepare_digest(session, load_data_from_json):
    load_data_from_json("data_set01.json")
    await prepare_digest(user_id=3)

    last_digest = session.scalars(select(Digest).order_by(Digest.id.desc())).first()
    # all_digests = session.scalars(select(Digest)).all()
    # print(f"{all_digests=}")
    assert last_digest.user_id == 3
    assert len(last_digest.posts) == 2
    assert 6 in [post.post_id for post in last_digest.posts]
    assert 8 in [post.post_id for post in last_digest.posts]
