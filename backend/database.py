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


@stub.function(keep_warm=1, max_concurrent_inputs=1000, concurrency_limit=1)
@modal.asgi_app()
def api():
    from sqlalchemy import and_, or_

    from . import models

    api = FastAPI()

    def connect():
        import os

        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        user = os.environ["PGUSER"]
        password = os.environ["PGPASSWORD"]
        host = os.environ["PGHOST"]
        port = os.environ["PGPORT"]
        database = os.environ["PGDATABASE"]

        connection_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"

        engine = create_engine(connection_string, echo=True)

        Session = sessionmaker(bind=engine)
        session = Session()

        return session

    db = connect()

    api.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @api.post("/users/", response_model=models.UserRead)
    def create_user(user: models.UserCreate):
        user = models.User(**user.dict())
        db.add(user)
        db.commit()

        user = models.UserRead(**user.__dict__)

        return user

    @api.get("/users/", response_model=List[models.UserRead])
    def read_users():
        return [
            models.UserRead(**user.__dict__) for user in db.query(models.User).all()
        ]

    @api.get("/users/{user_id}")
    def read_user(user_id: int) -> Optional[models.UserRead]:
        return models.UserRead(**db.query(models.User).get(user_id).__dict__)

    @api.get("/users/{user_id}/tweets/", response_model=List[models.TweetRead])
    def read_user_tweets(user_id: int):
        user = db.query(models.User).get(user_id)
        return [models.TweetRead(**tweet.__dict__) for tweet in user.tweets]

    @api.get("/names/{user_name}")
    def read_user_by_name(user_name: str) -> Optional[models.UserRead]:
        return db.query(models.User).filter(models.User.user_name == user_name).first()

    @api.post("/tweet/", response_model=models.TweetRead)
    def create_tweet(tweet: models.TweetCreate):
        # convert TweetCreat to the ORM Tweet Object
        tweet_model = models.Tweet(**tweet.dict())
        db.add(tweet_model)
        db.commit()
        db.refresh(tweet_model)
        return tweet_model

    @api.get("/tweets/", response_model=List[models.TweetRead])
    def read_tweets():
        return db.query(models.Tweet).all()

    @api.post("/timeline/", response_model=List[models.TweetRead])
    def read_timeline(
        real_time: datetime, user_id: Optional[int] = None, limit: int = 10
    ):
        fake_time = to_fake(real_time)
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
                        models.Tweet.fake_time == None,
                    ),
                )
            )
        posts_query = (
            posts_query.order_by(models.Tweet.fake_time.desc()).limit(limit).all()
        )
        if not posts_query:
            raise fastapi.HTTPException(
                status_code=404, detail="No tweets found in the timeline"
            )
        # TODO: increment views
        return [models.TweetRead(**post.__dict__) for post in posts_query]

    @api.post("/posts/", response_model=List[models.TweetRead])
    def read_posts(real_time: datetime, user_id: int, limit: int = 10):
        fake_time = to_fake(real_time)
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
            .order_by(models.Tweet.fake_time.desc())
            .limit(limit)
            .all()
        )
        # TODO: increment views
        return [models.TweetRead(**post.__dict__) for post in posts]

    @api.post("/profile", response_model=models.ProfileRead)
    def read_profile(user_id: int):
        user = db.query(models.User).get(user_id)
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
