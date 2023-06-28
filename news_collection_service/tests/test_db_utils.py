import pytest
from news_collection_service.db_utils import add_post_async
from shared.models import Channel, Post


@pytest.fixture(scope="module")
def create_object(session):
    def _create_object(object_type, object_data):
        obj = object_type(**object_data)
        session.add(obj)
        session.commit()
        return obj

    return _create_object


def test_create_channel_with_posts(session, create_object):
    channel_data = {
        'channel_name': "test Channel-1",
        'channel_username': "Channel-1 username",
        'posts': [
            Post(title="Post-1 from Channel-1", content="Content for Post-1"),
            Post(title="Post-2 from Channel-1", content="Content for Post-2"),
            Post(title="Post-3 from Channel-1", content="Content for Post-3"),
            Post(title="Post-4 from Channel-1", content="Content for Post-4"),
        ]
    }
    channel = create_object(Channel, channel_data)
    channel_from_db = session.query(Channel).first()
    post_from_db = session.query(Post).get(2)

    assert channel.channel_name == channel_from_db.channel_name
    assert post_from_db.title == channel_data["posts"][2].title


def test_add_post_async(session, create_object):
    pass
