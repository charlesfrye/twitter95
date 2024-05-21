import datetime

from sqlalchemy import (
    CheckConstraint,
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Table,
    Text,
)
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, relationship

from .utils import to_fake


class Base(AsyncAttrs, DeclarativeBase):
    pass


followers_association = Table(
    "followers",
    Base.metadata,
    Column("follower_id", Integer, ForeignKey("users.user_id"), primary_key=True),
    Column("followed_id", Integer, ForeignKey("users.user_id"), primary_key=True),
)

likes_association = Table(
    "likes",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.user_id"), primary_key=True),
    Column("tweet_id", Integer, ForeignKey("tweets.tweet_id"), primary_key=True),
)

replies_association = Table(
    "replies",
    Base.metadata,
    Column("tweet_id", Integer, ForeignKey("tweets.tweet_id"), primary_key=True),
    Column("reply_tweet_id", Integer, ForeignKey("tweets.tweet_id"), primary_key=True),
)


class Tweet(Base):
    __tablename__ = "tweets"
    __table_args__ = (CheckConstraint("views >= 0", name="check_views_non_negative"),)

    tweet_id = Column(Integer, primary_key=True, autoincrement=True)
    author_id = Column(Integer, ForeignKey("users.user_id"))
    text = Column(Text)
    fake_time = Column(DateTime, default=lambda: to_fake(datetime.datetime.utcnow()))
    real_time = Column(DateTime, default=datetime.datetime.utcnow)
    quoted = Column(Integer, ForeignKey("tweets.tweet_id"), nullable=True)


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(String, unique=True)
    display_name = Column(String)
    profile_pic = Column(String, default="")


class Bio(Base):
    __tablename__ = "bios"

    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)
    content = Column(Text, default="")
    location = Column(String, default="Earth")

    user = relationship("User", back_populates="bio", uselist=False)


User.bio = relationship("Bio", back_populates="user", uselist=False)
