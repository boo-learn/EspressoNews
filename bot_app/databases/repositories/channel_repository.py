from typing import Optional
from shared.database import async_session
from shared.models import Channel
from sqlalchemy.exc import SQLAlchemyError


class ChannelRepository:
    def __init__(self):
        self.session = async_session()

    def create(self, **kwargs) -> Channel:
        try:
            channel = Channel(**kwargs)
            self.session.add(channel)
            self.session.commit()
            return channel
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e

    def get(self, channel_username: str) -> Optional[Channel]:
        try:
            return self.session.query(Channel).filter_by(channel_username=channel_username).first()
        except SQLAlchemyError as e:
            raise e

    def delete(self, channel: Channel):
        try:
            self.session.delete(channel)
            self.session.commit()
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
