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
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

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
    fake_time = Column(DateTime)
    real_time = Column(DateTime, default=datetime.datetime.utcnow)
    liked_by = relationship("User", secondary=likes_association, backref="likes")
    replies = relationship(
        "Tweet",
        secondary=replies_association,
        primaryjoin=tweet_id == replies_association.c.tweet_id,
        secondaryjoin=tweet_id == replies_association.c.reply_tweet_id,
        backref="replied_to",
    )
    quoted = Column(Integer, ForeignKey("tweets.tweet_id"), nullable=True)
    retweeted = Column(Integer, ForeignKey("tweets.tweet_id"), nullable=True)
    images = Column(ARRAY(String))
    root = Column(Integer, ForeignKey("tweets.tweet_id"), nullable=True)
    views = Column(Integer, default=0)

    user = relationship("User", back_populates="tweets")


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(String)  # TODO: make unique
    display_name = Column(String)
    profile_pic = Column(String, default="")
    banner_pic = Column(String, default="")
    follows = relationship(
        "User",
        secondary=followers_association,
        primaryjoin=user_id == followers_association.c.follower_id,
        secondaryjoin=user_id == followers_association.c.followed_id,
        backref="followers",
    )

    tweets = relationship("Tweet", back_populates="user")


class Bio(Base):
    __tablename__ = "bios"

    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)
    content = Column(Text, default="")
    location = Column(String, default="Earth")
    birthday = Column(DateTime)
    joined_on = Column(DateTime)

    user = relationship("User", back_populates="bio", uselist=False)


User.bio = relationship("Bio", back_populates="user", uselist=False)


from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class UserBase(BaseModel):
    user_name: str
    display_name: str
    profile_pic: Optional[str] = None
    banner_pic: Optional[str] = None


class UserCreate(UserBase):
    pass


class UserRead(UserBase):
    user_id: int
    tweets: List["TweetRead"] = []

    class Config:
        orm_mode = True


class TweetBase(BaseModel):
    text: str
    author_id: Optional[int] = None
    fake_time: Optional[datetime] = None
    real_time: Optional[datetime] = None
    images: Optional[List[str]] = None
    views: Optional[int] = 0


class TweetCreate(TweetBase):
    pass


class TweetRead(TweetBase):
    tweet_id: int
    root: Optional[int] = None

    class Config:
        orm_mode = True


class BioBase(BaseModel):
    content: Optional[str] = ""
    location: Optional[str] = "Earth"
    birthday: Optional[datetime] = None
    joined_on: Optional[datetime] = None


class BioRead(BioBase):
    user_id: int

    class Config:
        orm_mode = True


class ProfileRead(BaseModel):
    user: UserRead
    bio: BioRead

    class Config:
        orm_mode = True


UserRead.update_forward_refs()
TweetRead.update_forward_refs()
