from datetime import datetime, timezone

import modal

from .common import image

nyt_image = image.pip_install("pandas", "requests")
volume = modal.Volume.from_name("nyt-bot-volume", create_if_missing=True)

stub = modal.Stub(
    "nyt_bot",
    # secrets=[modal.Secret.from_name("nyt-api-key")],
    image=nyt_image,
    volumes={"/archive": volume},
)

with nyt_image.imports():
    import pandas as pd
    import requests

    from . import models


@stub.function(_allow_background_volume_commits=True)
def go():
    user = create_or_fetch_user()
    df = load_articles()
    add_tweets(df, user)


def add_tweets(df, user):
    for index, row in df.iterrows():
        tweet = models.TweetCreate(
            author=user,
            text=row["headline"],
            fake_time=generate_faketime_utc_timestamp(
                row["pub_date"], calculate_publish_hour(index, len(df))
            ),
        )
        try:
            response = requests.post(
                "https://ex-twitter--db-client-api.modal.run/tweets/", json=tweet.dict()
            )
            response.raise_for_status()
        except Exception as e:
            print(f"error posting tweet {index}")
            print(e)


def load_articles(day=None):
    file = "/archive/new_york_times_stories_1995_april.csv"
    df = pd.read_csv(file)
    df = df[["headline", "word_count", "url", "pub_date"]]
    if day is None:
        day = datetime.utcnow().day
    articles = df[df["pub_date"] == f"1995-04-{day.zfill(2)}T05:00:00+0000"]

    return articles


def generate_faketime_utc_timestamp(date, hour) -> datetime:
    """returns the datetime object for the given date and hour in UTC"""
    naive_datetime = datetime.strptime(f"{date} {hour}:00:00", "%Y-%m-%d %H:%M:%S")
    utc_datetime = naive_datetime.replace(tzinfo=timezone.utc)
    return utc_datetime


def calculate_publish_hour(article_index, total_articles, start_index=0):
    if total_articles == 0:
        raise ValueError("Total articles must be greater than 0")

    normalized_index = article_index - start_index
    hours_in_day = 24

    articles_per_hour = total_articles / hours_in_day

    publish_hour = int(normalized_index / articles_per_hour)

    publish_hour = min(publish_hour, hours_in_day - 1)

    return publish_hour


def create_or_fetch_user():
    userName = "NewYorkTimes"
    try:
        response = requests.get(
            f"https://ex-twitter--db-client-api.modal.run/names/{userName}"
        )
        response.raise_for_status()
        data = response.json()
        if data is None:
            print(f"User {userName} not found. Creating...")
            return create_user()
        else:
            user = models.UserRead(**data)
            return user
    except requests.exceptions.HTTPError as e:
        print(e)
        raise


def create_user():
    create_req = models.UserCreate(
        profile_pic="https://1000logos.net/wp-content/uploads/2017/04/New-York-Times-emblem.jpg",
        banner_pic="https://1000logos.net/wp-content/uploads/2017/04/Font-New-York-Times-Logo.jpg",
        user_name="NewYorkTimes",
        display_name="New York Times Newspaper",
    )

    try:
        response = requests.post(
            "https://ex-twitter--db-client-api.modal.run/users/", json=create_req.dict()
        )
        response.raise_for_status()
        user = models.UserRead(**response.json())
        return user
    except Exception as e:
        print(e)
        raise


@stub.local_entrypoint()
def main():
    go.remote()
