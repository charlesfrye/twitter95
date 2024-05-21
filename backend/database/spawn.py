from pathlib import Path

import modal

from .common import image

stub = modal.Stub(
    "pgsql", image=image, secrets=[modal.Secret.from_name("pgsql-secret")]
)

with image.imports():
    from .models import Base, Tweet, User


def test(session):
    all_tweets = session.query(Tweet).all()
    for tweet in all_tweets:
        print(f"Tweet: {tweet.text} by User ID: {tweet.author_id}")
        for reply in tweet.replies:
            print(f"Reply: {reply.text}")


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
    # Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    return session


@stub.function(
    mounts=[
        modal.Mount.from_local_dir(Path(__file__).parent / "data", remote_path="/data")
    ]
)
def go():
    session = connect()
    create(session)
    # test(session)
    session.close()


@stub.local_entrypoint()
def main():
    go.remote()
