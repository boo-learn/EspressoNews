import pytest
import os
import asyncio
import pytest_asyncio
from shared.models import User, Channel, Post, Subscription, Digest
from sqlalchemy import select, func
from digest_service.digest_main import prepare_digest, create_digest


@pytest.fixture(scope='session')
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Mark all test as asyncio
# pytestmark = pytest.mark.asyncio


# @pytest.mark.skip()
def test_create_digest(session, load_data_from_json):
    load_data_from_json("data_set01.json")
    digest = session.scalar(select(Digest))
    assert digest.user_id == 3
    assert digest.posts[0].post_id == 9
    assert digest.posts[1].post_id == 10


# @pytest.mark.skip()
@pytest.mark.asyncio
async def test_prepare_digest(event_loop, session, load_data_from_json):
    load_data_from_json("data_set01.json")
    await create_digest(user_id=3)

    last_digest = session.scalars(select(Digest).order_by(Digest.id.desc())).first()
    # all_digests = session.scalars(select(Digest)).all()
    # print(f"{all_digests=}")
    assert last_digest.user_id == 3
    assert len(last_digest.posts) == 2
    assert 6 in [post.post_id for post in last_digest.posts]
    assert 8 in [post.post_id for post in last_digest.posts]


@pytest.mark.asyncio
async def test_digest_not_created_for_empty_posts(event_loop, session, load_data_from_json):
    load_data_from_json("data_set02.json")
    num_digests_before = session.query(func.count(Digest.id)).scalar()
    assert num_digests_before == 3
    await create_digest(user_id=1)
    await create_digest(user_id=3)
    num_digests_after = session.query(func.count(Digest.id)).scalar()
    last_digest = session.scalars(select(Digest).order_by(Digest.id.desc())).first()
    print(last_digest)
    assert num_digests_after == 3
    assert last_digest.id == 3
