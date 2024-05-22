from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UserBase(BaseModel):
    user_name: str
    display_name: str
    profile_pic: Optional[str] = None


class UserRead(UserBase):
    user_id: int

    class Config:
        orm_mode = True


class TweetBase(BaseModel):
    text: str
    author_id: Optional[int] = None
    fake_time: Optional[datetime] = None
    real_time: Optional[datetime] = None
    quoted: Optional[int] = None


class TweetCreate(TweetBase):
    pass


class TweetRead(TweetBase):
    tweet_id: int

    class Config:
        orm_mode = True


class FullTweetRead(TweetRead):
    author: UserRead
    quoted_tweet: Optional["FullTweetRead"] = None


class BioBase(BaseModel):
    content: Optional[str] = ""
    location: Optional[str] = "Earth"


class BioRead(BioBase):
    user_id: int

    class Config:
        orm_mode = True


class UserCreate(UserBase):
    bio: Optional[BioBase] = None


class ProfileRead(BaseModel):
    user: UserRead
    bio: BioRead

    class Config:
        orm_mode = True


UserRead.update_forward_refs()
TweetRead.update_forward_refs()
