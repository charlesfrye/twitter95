from pathlib import Path

import modal

from .common import image

stub = modal.Stub(
    "pgsql", image=image, secrets=[modal.Secret.from_name("pgsql-secret")]
)

with image.imports():
    from .models import Base, Tweet, User


def create(session):
    # special_5 = read_jsonl("/data/special-5.jsonl")
    # for element in special_5:
    #     print(element)
    #     # user, bio = load_persona(element, session)
    #     print(user.__dict__)
    #     print(bio.__dict__)
    # user.follows.append()
    # session.add(user)
    # session.add(bio)
    # session.commit()

    # nyt = session.get(User, 3)
    # for ii in range(4, 9):
    #     user = session.get(User, ii)
    #     print(user.__dict__)

    try:
        # Get the user who will be followed (user with ID 3)
        nyt = session.get(User, 3)
        if not nyt:
            print("User with ID 3 not found.")
            raise ValueError("Target user not found in the database.")

        follower_ids = range(4, 9)
        followers = session.query(User).filter(User.user_id.in_(follower_ids)).all()

        if len(followers) < len(follower_ids):
            missing_ids = set(follower_ids) - {user.user_id for user in followers}
            print(f"Warning: Some users not found, IDs: {missing_ids}")

        for follower in followers:
            if nyt not in follower.follows:
                follower.follows.append(nyt)

        session.commit()
        print("All specified users now follow the user with ID 3.")
    except Exception as e:
        session.rollback()
        print(f"An error occurred: {e}")
    finally:
        session.close()

    # connect them all to each other

    # user1.follows.append(user2)
    # user2.follows.append(user1)
    # session.commit

    # tweet1 = Tweet(author_id=user1.user_id, text=user1.bio.content)
    # tweet2 = Tweet(author_id=user2.user_id, text="yuo are dumb", replied_to=[tweet1])
    # session.add(tweet1)
    # session.add(tweet2)
    # session.commit()


def read_jsonl(file):
    import json

    with open(file, "r", encoding="utf-8") as f:
        for line in f:
            yield json.loads(line)


def load_persona(element, session):
    from . import models

    user = models.User(user_name=slugify(element["name"]), display_name=element["name"])
    session.add(user)
    session.commit()
    bio = models.Bio(user_id=user.user_id, content=element["bio"])
    session.add(bio)
    session.commit()

    return user, bio


def slugify(text):
    return text.lower().replace(" ", "_")


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
