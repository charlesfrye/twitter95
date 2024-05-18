import os
from datetime import datetime
from typing import List, Optional

import fastapi
import modal
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .common import image


stub = modal.Stub(
    "db-client", image=image, secrets=[modal.Secret.from_name("pgsql-secret")]
)


@stub.function(keep_warm=1, allow_concurrent_inputs=1000, concurrency_limit=1)
@modal.asgi_app()
def api():
    from sqlalchemy import and_, desc, or_
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

        user = models.UserRead(**user.__dict__)

        return user

    @api.get("/users/", response_model=List[models.UserRead])
    async def read_users():
        async with new_session() as db:
            users = await db.scalars(
                select(models.User).order_by(desc(models.User.user_id))
            )

            return [models.UserRead(**user.__dict__) for user in users]

    @api.get("/users/{user_id}")
    async def read_user(user_id: int) -> Optional[models.UserRead]:
        async with new_session() as db:
            result = await db.execute(select(models.User).filter_by(user_id=user_id))
            user = result.scalar_one_or_none()
        if user is None:
            return None
        return models.UserRead(**user.__dict__)

    @api.get("/users/{user_id}/tweets/", response_model=List[models.TweetRead])
    async def read_user_tweets(user_id: int):
        async with new_session() as db:
            result = await db.execute(select(models.User).filter_by(user_id=user_id))
            user = result.scalar_one_or_none()
            if user is None:
                raise FastAPI.HTTPException(status_code=404, detail="User not found")

            tweets = await user.awaitable_attrs.tweets
        return [models.TweetRead.from_orm(tweet) for tweet in reversed(tweets)]

    @api.get("/names/{user_name}")
    async def read_user_by_name(user_name: str) -> Optional[models.UserRead]:
        async with new_session() as db:
            result = await db.execute(
                select(models.User).filter_by(user_name=user_name)
            )
            user = result.scalar_one_or_none()
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
    async def read_tweets(limit=10):
        async with new_session() as db:
            result = await db.execute(
                select(models.Tweet).order_by(desc(models.Tweet.fake_time)).limit(limit)
            )
            tweets = result.scalars()
            return [models.TweetRead(**tweet.__dict__) for tweet in tweets]

    @api.post("/timeline/", response_model=List[models.TweetRead])
    async def read_timeline(
        real_time: datetime, user_id: Optional[int] = None, limit: int = 10
    ):
        # TODO: why is user_id optional?
        # TODO: set up fake/real time
        fake_time = to_fake(real_time)
        with new_session() as db:
            posts_query = db.query(models.Tweet).join(
                models.followers_association,
                models.followers_association.c.followed_id == models.Tweet.author_id,
            )
            if user_id is not None:
                # get tweets from users that the user follows
                posts_query = posts_query.filter(
                    and_(
                        models.followers_association.c.follower_id == user_id,
                        or_(
                            models.Tweet.fake_time <= fake_time,
                            models.Tweet.fake_time == None,  # noqa: E711
                        ),
                    )
                )
            posts_query = (
                posts_query.order_by(models.Tweet.fake_time.asc()).limit(limit).all()
            )
            if not posts_query:
                raise fastapi.HTTPException(
                    status_code=404, detail="No tweets found in the timeline"
                )
        return [models.TweetRead(**post.__dict__) for post in posts_query]

    @api.post("/posts/", response_model=List[models.TweetRead])
    def read_posts(real_time: datetime, user_id: int, limit: int = 10):
        fake_time = to_fake(real_time)
        with new_session() as db:
            posts = (
                db.query(models.Tweet)
                .filter(
                    and_(
                        or_(
                            models.Tweet.fake_time <= fake_time,
                            models.Tweet.fake_time == None,  # noqa: E711
                        ),
                    ),
                    models.Tweet.author_id == user_id,
                )
                .order_by(models.Tweet.fake_time.asc())
                .limit(limit)
                .all()
            )
        return [models.TweetRead(**post.__dict__) for post in posts]

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
                user=models.UserRead(**user.__dict__),
                bio=models.BioRead(user_id=user_id),
            )
        return models.ProfileRead(
            user=models.UserRead(**user.__dict__),
            bio=models.BioRead(**bio.__dict__),
        )

    return api


def to_fake(real_time: datetime) -> datetime:
    return real_time
