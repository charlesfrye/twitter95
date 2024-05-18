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
    from sqlalchemy import and_, desc, or_, select

    from . import models

    api = FastAPI(
        title="twitter95",
        summary="What if Twitter was made in 1995?",
        version="0.1.0",
        docs_url="/",
        redoc_url=None,
    )

    def connect():
        import os

        from sqlalchemy import create_engine

        user = os.environ["PGUSER"]
        password = os.environ["PGPASSWORD"]
        host = os.environ["PGHOST"]
        port = os.environ["PGPORT"]
        database = os.environ["PGDATABASE"]

        connection_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"

        engine = create_engine(
            connection_string,
            isolation_level="READ COMMITTED",  # default and lowest level in pgSQL
            echo=True,  # log SQL as it is emitted
        )

        return engine

    engine = connect()

    def new_session():
        from sqlalchemy.orm import sessionmaker

        Session = sessionmaker(bind=engine)
        session = Session()

        return session

    api.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @api.post("/users/", response_model=models.UserRead)
    def create_user(user: models.UserCreate):
        with new_session() as db:
            user = models.User(**user.dict())
            db.add(user)
            db.commit()

        user = models.UserRead(**user.__dict__)

        return user

    @api.get("/users/", response_model=List[models.UserRead])
    def read_users():
        with new_session() as db:
            users = db.scalars(select(models.User).order_by(desc(models.User.user_id)))

            return [models.UserRead(**user.__dict__) for user in users]

    @api.get("/users/{user_id}")
    def read_user(user_id: int) -> Optional[models.UserRead]:
        with new_session() as db:
            user = db.execute(
                select(models.User).filter_by(user_id=user_id)
            ).scalar_one_or_none()
        if user is None:
            return None
        return models.UserRead(**user.__dict__)

    @api.get("/users/{user_id}/tweets/", response_model=List[models.TweetRead])
    def read_user_tweets(user_id: int):
        with new_session() as db:
            user = db.execute(
                select(models.User).filter_by(user_id=user_id)
            ).scalar_one_or_none()
            tweets = user.tweets
        return [models.TweetRead(**tweet.__dict__) for tweet in tweets]

    @api.get("/names/{user_name}")
    def read_user_by_name(user_name: str) -> Optional[models.UserRead]:
        with new_session() as db:
            user = db.execute(
                select(models.User).filter_by(user_name=user_name)
            ).scalar_one_or_none()
        return user

    @api.post("/tweet/", response_model=models.TweetRead)
    def create_tweet(tweet: models.TweetCreate):
        tweet_model = models.Tweet(**tweet.dict())
        with new_session() as db:
            db.add(tweet_model)
            db.commit()
            db.refresh(tweet_model)
        return tweet_model

    @api.get("/tweets/", response_model=List[models.TweetRead])
    def read_tweets(limit=10):
        with new_session() as db:
            tweets = db.execute(
                select(models.Tweet).order_by(desc(models.Tweet.fake_time)).limit(limit)
            ).scalars()
            return [models.TweetRead(**tweet.__dict__) for tweet in tweets]

    @api.post("/timeline/", response_model=List[models.TweetRead])
    def read_timeline(
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
    def read_profile(user_id: int):
        with new_session() as db:
            user = db.query(models.User).get(user_id)
        with new_session() as db:
            bio = db.query(models.Bio).get(user_id)
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
