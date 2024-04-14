import modal
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from typing import List

from .common import image


stub = modal.Stub(
    "db-client", image=image, secrets=[modal.Secret.from_name("pgsql-secret")]
)


@stub.function()
@modal.asgi_app()
def api():
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
        # models.Base.metadata.create_all(engine)

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
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @api.get("/users/", response_model=List[models.UserRead])
    def read_users():
        return db.query(models.User).all()

    @api.post("/tweets/", response_model=models.TweetRead)
    def create_tweet(tweet: models.TweetCreate):
        db.add(tweet)
        db.commit()
        db.refresh(tweet)
        return tweet

    @api.get("/tweets/", response_model=List[models.TweetRead])
    def read_tweets():
        return db.query(models.Tweet).all()

    return api
