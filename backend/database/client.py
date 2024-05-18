import os
from datetime import datetime, timedelta
from typing import List, Optional

import fastapi
import modal
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .common import image


app = modal.App(
    "db-client",
    image=image,
    secrets=[modal.Secret.from_name("pgsql-secret")],
)


@app.function(keep_warm=1, allow_concurrent_inputs=1000, concurrency_limit=1)
@modal.asgi_app()
def api():
    from sqlalchemy import and_, asc, desc, or_
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.future import select
    from sqlalchemy.orm import sessionmaker

    from . import models

    api = FastAPI(
        title="twitter95",
        summary="What if Twitter was made in 1995?",
        version="0.1.0",
        docs_url="/",
        redoc_url=None,
    )

    def connect():
        user = os.environ["PGUSER"]
        password = os.environ["PGPASSWORD"]
        host = os.environ["PGHOST"]
        port = os.environ["PGPORT"]
        database = os.environ["PGDATABASE"]

        connection_string = (
            f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}"
        )

        engine = create_async_engine(
            connection_string,
            isolation_level="READ COMMITTED",  # default and lowest level in pgSQL
            echo=True,  # log SQL as it is emitted
        )

        return engine

    engine = connect()

    new_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    api.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @api.post("/users/", response_model=models.UserRead)
    async def create_user(user: models.UserCreate):
        async with new_session() as db:
            user = models.User(**user.dict())
            db.add(user)
            await db.commit()
            await db.refresh(user)

        # TODO: from_orm
        user = models.UserRead(**user.__dict__)

        return user

    @api.get("/users/", response_model=List[models.UserRead])
    async def read_users(ascending: bool = False):
        async with new_session() as db:
            users = await db.scalars(
                select(models.User).order_by(
                    models.User.user_id if ascending else desc(models.User.user_id)
                )
            )

        return [models.UserRead.from_orm(user) for user in users]

    @api.get("/users/{user_id}")
    async def read_user(user_id: int) -> Optional[models.UserRead]:
        async with new_session() as db:
            result = await db.execute(select(models.User).filter_by(user_id=user_id))
            user = result.scalar_one_or_none()
        if user is None:
            raise fastapi.HTTPException(
                status_code=404, detail=f"User {user_id} not found"
            )
        return models.UserRead.from_orm(user)

    @api.get("/users/{user_id}/tweets/", response_model=List[models.TweetRead])
    async def read_user_tweets(user_id: int, limit=10):
        async with new_session() as db:
            result = await db.execute(select(models.User).filter_by(user_id=user_id))
            user = result.scalar_one_or_none()
            if user is None:
                raise fastapi.HTTPException(
                    status_code=404, detail=f"User {user_id} not found"
                )

            result = await db.scalars(
                select(models.Tweet)
                .filter_by(author_id=user_id)
                .order_by(desc(models.Tweet.fake_time), desc(models.Tweet.tweet_id))
                .limit(limit)
            )
            tweets = result.all()

        return [models.TweetRead.from_orm(tweet) for tweet in tweets]

    @api.get("/names/{user_name}")
    async def read_user_by_name(user_name: str) -> Optional[models.UserRead]:
        async with new_session() as db:
            result = await db.execute(
                select(models.User).filter_by(user_name=user_name)
            )
            user = result.scalar_one_or_none()
            if user is None:
                raise fastapi.HTTPException(
                    status_code=404, detail=f"User {user_name} not found"
                )
        return user

    @api.post("/tweet/", response_model=models.TweetRead)
    async def create_tweet(tweet: models.TweetCreate):
        tweet_model = models.Tweet(**tweet.dict())
        async with new_session() as db:
            db.add(tweet_model)
            await db.commit()
            await db.refresh(tweet_model)
        return tweet_model

    @api.get("/tweets/", response_model=List[models.TweetRead])
    async def read_tweets(limit=10, ascending: bool = False):
        sort = asc if ascending else desc
        async with new_session() as db:
            result = await db.execute(
                select(models.Tweet)
                .order_by(sort(models.Tweet.fake_time), sort(models.Tweet.tweet_id))
                .limit(limit)
            )
            tweets = result.scalars()
        return [models.TweetRead.from_orm(tweet) for tweet in tweets]

    @api.post("/timeline/", response_model=List[models.TweetRead])
    async def read_timeline(
        real_time: datetime, user_id: int, limit: int = 10, ascending=False
    ):
        fake_time = to_fake(real_time)
        sort = asc if ascending else desc
        async with new_session() as db:
            followed_users = select(models.followers_association.c.followed_id).where(
                models.followers_association.c.follower_id == user_id
            )

            result = await db.execute(
                select(models.Tweet)
                .where(models.Tweet.author_id.in_(followed_users))
                .filter(
                    and_(
                        or_(
                            models.Tweet.fake_time <= fake_time,
                            models.Tweet.fake_time == None,  # noqa: E711
                        ),
                    )
                )
                .order_by(sort(models.Tweet.fake_time), sort(models.Tweet.tweet_id))
                .limit(limit)
            )

            tweets = result.scalars()
        return [models.TweetRead.from_orm(tweet) for tweet in tweets]

    @api.post("/posts/", response_model=List[models.TweetRead])
    async def read_posts(
        real_time: datetime, user_id: int, limit: int = 10, ascending=False
    ):
        fake_time = to_fake(real_time)
        sort = asc if ascending else desc
        async with new_session() as db:
            results = await db.execute(
                select(models.Tweet)
                .filter(
                    and_(
                        or_(
                            models.Tweet.fake_time <= fake_time,
                            models.Tweet.fake_time == None,  # noqa: E711
                        ),
                    ),
                    models.Tweet.author_id == user_id,
                )
                .order_by(sort(models.Tweet.fake_time), sort(models.Tweet.tweet_id))
                .limit(limit)
            )
            posts = results.scalars()
        return [models.TweetRead.from_orm(post) for post in posts]

    @api.post("/profile", response_model=models.ProfileRead)
    async def read_profile(user_id: int):
        async with new_session() as db:
            result = await db.execute(select(models.User).filter_by(user_id=user_id))
            user = result.scalar_one_or_none()
            if user is None:
                return FastAPI.HTTPException(status_code=404, detail="User not found")
            bio = await user.awaitable_attrs.bio
        if bio is None:
            return models.ProfileRead(
                user=models.UserRead.from_orm(user),
                bio=models.BioRead(user_id=user_id),
            )
        return models.ProfileRead(
            user=models.UserRead.from_orm(user),
            bio=models.BioRead.from_orm(bio),
        )

    return api


def to_fake(real_time: datetime) -> datetime:
    delta = timedelta(seconds=915_235_088)  # rough number of seconds from 1995 to 2024
    fake_time = real_time - delta
    fake_time = fake_time.replace(tzinfo=None)
    return fake_time
