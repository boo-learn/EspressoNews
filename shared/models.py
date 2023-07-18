from datetime import datetime
from typing import List
from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Enum, Text, LargeBinary, \
    BigInteger, Table
from sqlalchemy import Column, Integer, String, JSON, DateTime, Float
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from shared.database import Base
from shared.selection_values_for_models import RoleEnum, IntonationEnum, PeriodicityEnum


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
    settings = relationship("UserSettings", back_populates="user", uselist=False)
    digests: Mapped[List["Digest"]] = relationship(back_populates="user")
    # access_channels = relationship("Channel", back_populates="user")


# Parent
class Role(Base):
    __tablename__ = "roles"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name = Mapped[str]
    gpt_system_content = Mapped[str]
    gpt_user_content = Mapped[str]
    # posts = relationship('User', back_populates='role')
    user_settings: Mapped[List["UserSettings"]] = relationship(back_populates="role")


# Child
class UserSettings(Base):
    __tablename__ = 'user_settings'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))

    periodicity = Column(Enum(PeriodicityEnum), default=PeriodicityEnum.FOR_TEST)
    user = relationship("User", back_populates="settings")
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"))
    role: Mapped["Role"] = relationship(back_populates="user_settings")


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
    channel_name = Column(String, nullable=False)
    channel_username = Column(String(50), nullable=False)
    channel_description = Column(Text, nullable=True)
    member_count = Column(Integer, nullable=True)
    channel_invite_link = Column(String(65), nullable=True)
    account_id = Column(BigInteger, ForeignKey('telegram_accounts.account_id'))  # Add this line

    is_active = Column(Boolean, default=True)

    # user = relationship("User", back_populates="access_channels")
    subscriptions = relationship('Subscription', back_populates='channel', cascade='all, delete-orphan')
    posts = relationship('Post', back_populates='channel')
    telegram_account = relationship("TelegramAccount", back_populates="channels")


digests_posts = Table(
    "digests_posts",
    Base.metadata,
    Column("digest_id", ForeignKey("digests.id"), primary_key=True),
    Column("post_id", ForeignKey("posts.post_id"), primary_key=True),
)


class DigestAssociation(Base):
    __table__ = digests_posts
    digest: Mapped["Digest"] = relationship('Digest', back_populates="digest_recs")


class Digest(Base):
    __tablename__ = 'digests'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))
    user: Mapped["User"] = relationship(back_populates="digests")
    posts: Mapped[List["Post"]] = relationship(secondary=digests_posts, viewonly=True)
    # generation_date = Column(DateTime, nullable=False, default=datetime.now)
    generation_date: Mapped[datetime] = mapped_column(insert_default=func.now())
    total_summary: Mapped[Optional[str]]
    digest_recs: Mapped[list["DigestAssociation"]] = relationship("DigestAssociation", back_populates="digest",
                                                                  cascade="all, delete-orphan")
    digest_ids: Mapped[list[int]] = association_proxy(
        "digest_recs", "post_id",
        creator=lambda uid: DigestAssociation(post_id=uid))

    def __repr__(self):
        return f"Digest id={self.id} post_ids={[post.post_id for post in self.posts]}"


class Post(Base):
    __tablename__ = 'posts'

    post_id = Column(BigInteger, primary_key=True, unique=True)
    channel_id = Column(BigInteger, ForeignKey('channels.channel_id'))
    rubric_id = Column(Integer, ForeignKey('posts_rubrics.rubric_id'), nullable=True)

    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    # summary = Column(Text, nullable=True)
    summaries: Mapped[List["Summary"]] = relationship(back_populates="post")

    post_date = Column(DateTime, nullable=False, default=datetime.now)

    channel = relationship('Channel', back_populates='posts')
    rubric = relationship('Rubric', back_populates='posts')
    files = relationship('File', back_populates='post')


class Summary(Base):
    __tablename__ = 'summaries'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    content = Mapped[str]
    for_role = Mapped[str]
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.post_id"))
    post: Mapped["Post"] = relationship(back_populates="summaries")


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

    channels = relationship("Channel", back_populates="telegram_account")


class GPTAccount(Base):
    __tablename__ = 'gpt_accounts'

    account_id = Column(Integer, primary_key=True)
    api_key = Column(String(100))

    is_active = Column(Boolean, default=True)


class BeatSchedule(Base):
    __tablename__ = 'beat_schedule'

    id = Column(Integer, primary_key=True)
    task_name = Column(String, nullable=False)  # New field for the task name
    task = Column(String, nullable=False)  # Field for the task itself
    schedule = Column(Integer, nullable=False)
    args = Column(JSON, nullable=True)
    kwargs = Column(JSON, nullable=True)
    last_run_at = Column(DateTime, nullable=True)
    total_run_count = Column(Integer, default=0)
