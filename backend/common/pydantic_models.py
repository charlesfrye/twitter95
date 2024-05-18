from datetime import datetime
from typing import Optional

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

    class Config:
        orm_mode = True


class TweetBase(BaseModel):
    text: str
    author_id: Optional[int] = None
    fake_time: Optional[datetime] = None
    real_time: Optional[datetime] = None
    views: Optional[int] = 0


class TweetCreate(TweetBase):
    pass


class TweetRead(TweetBase):
    tweet_id: int

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
