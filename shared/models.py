from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, Text, LargeBinary, \
    PrimaryKeyConstraint, BigInteger
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    __tablename__ = 'users'

    user_id = Column(BigInteger, primary_key=True)
    username = Column(String(50), nullable=True)
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    language_code = Column(Enum('ru', 'en', name='language_code'), nullable=True)

    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    is_staff = Column(Boolean, default=False)

    join_date = Column(DateTime, nullable=True, default=datetime.now)

    subscriptions = relationship('Subscription', back_populates='user')
    # access_channels = relationship("Channel", back_populates="user")


class Subscription(Base):
    __tablename__ = 'subscriptions'

    # +
    user_id = Column(BigInteger, ForeignKey('users.user_id'), primary_key=True)
    channel_id = Column(BigInteger, ForeignKey('channels.channel_id'), primary_key=True)
    subscription_date = Column(DateTime, nullable=False, default=datetime.now)
    is_active = Column(Boolean, default=True)

    user = relationship('User', back_populates='subscriptions')
    channel = relationship('Channel', back_populates='subscriptions')


class Channel(Base):
    __tablename__ = 'channels'  # Change this line

    channel_id = Column(BigInteger, primary_key=True)
    # user_id = Column(Integer, ForeignKey('users.user_id'))  # Add this line
    channel_name = Column(String, nullable=False)
    channel_username = Column(String(50), nullable=False)
    channel_description = Column(Text, nullable=True)
    member_count = Column(Integer, nullable=True)
    channel_invite_link = Column(String(65), nullable=True)

    is_active = Column(Boolean, default=True)

    # user = relationship("User", back_populates="access_channels")
    subscriptions = relationship('Subscription', back_populates='channel')
    posts = relationship('Post', back_populates='channel')


class Post(Base):
    __tablename__ = 'posts'

    post_id = Column(BigInteger, primary_key=True, unique=True)
    channel_id = Column(BigInteger, ForeignKey('channels.channel_id'))
    rubric_id = Column(Integer, ForeignKey('posts_rubrics.rubric_id'), nullable=True)

    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)

    post_date = Column(DateTime, nullable=False)

    channel = relationship('Channel', back_populates='posts')
    rubric = relationship('Rubric', back_populates='posts')
    files = relationship('File', back_populates='post')


class Rubric(Base):
    __tablename__ = 'posts_rubrics'

    rubric_id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)

    posts = relationship('Post', back_populates='rubric')


class File(Base):
    __tablename__ = 'files_library'

    file_id = Column(Integer, primary_key=True)
    image = Column(LargeBinary, nullable=False)
    video = Column(LargeBinary, nullable=False)
    post_id = Column(Integer, ForeignKey('posts.post_id'))
    post = relationship('Post', back_populates='files')


class TelegramAccount(Base):
    __tablename__ = 'telegram_accounts'

    account_id = Column(BigInteger, primary_key=True)
    api_id = Column(Integer)
    api_hash = Column(String(100), nullable=False)
    phone_number = Column(String(15), nullable=False)
    session_string = Column(String, nullable=True)

    is_active = Column(Boolean, default=True)
    last_connected = Column(DateTime, nullable=False)


class GPTAccount(Base):
    __tablename__ = 'gpt_accounts'

    account_id = Column(Integer, primary_key=True)
    api_key = Column(String(100))

    is_active = Column(Boolean, default=True)
    last_connected = Column(DateTime, nullable=False)
