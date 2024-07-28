"""Shared configuration and behavior for NYT bots."""
import modal

import common
from bots.common import Client

from datetime import datetime
from pathlib import Path
from typing import Optional

BOT_PROFILE_PIC = (
    "https://1000logos.net/wp-content/uploads/2017/04/New-York-Times-emblem.jpg"
)

image = modal.Image.debian_slim(python_version="3.11").pip_install("pynytimes==0.10.0")
volume = modal.Volume.from_name("nyt-headlines", create_if_missing=True)

with image.imports():
    import json


ARCHIVE_ROOT = Path("/archive")

app = modal.App(
    "nyt_bot",
    secrets=[modal.Secret.from_name("nyt-api-secret")],
    image=image,
    volumes={ARCHIVE_ROOT: volume},
    mounts=[common.mount],
)


@app.function()
def get_or_create_bot_id(
    user_name: str,
    display_name: Optional[str] = None,
    profile_pic: Optional[str] = None,
):
    try:
        bot_user = Client.get_user_by_name.remote(user_name)
    except Exception:
        bot_user = Client.create_user.remote(
            user_name, display_name, profile_pic
        )  # TODO: handle optional?
    print(f"bot user: {bot_user}")
    return int(bot_user["user_id"])


def path_from_date(date: datetime):
    return ARCHIVE_ROOT / f"{date:%Y-%m}.json"


def get_articles_at_hour(hour: datetime):
    hour = hour.replace(minute=0, second=0, microsecond=0)
    with open(path_from_date(hour), "r") as f:
        archive = json.load(f)
    articles = []
    for article in archive:
        try:
            posted_time = datetime.fromisoformat(article["pub_date"]).replace(
                tzinfo=None
            )
        except KeyError:
            try:  # sometimes the pub_date is missing, but we have a web_url with a date
                web_url = article["web_url"]
                route = web_url.split("nytimes.com/")[1]
                y, m, d, *_ = route.split("/")
                posted_time = datetime.fromisoformat(f"{y}-{m}-{d}")
            except Exception:
                continue
        try:
            if posted_time == hour:
                print(article["lead_paragraph"][:20])
                articles.append(article)
        except KeyError:
            continue
    print(f"found {len(articles)} articles for {hour:%Y-%m-%d %H}")
    return articles


def parse_article(article):
    try:
        text = ""

        article_type = article["type_of_material"].upper()

        text += f"{article_type}: "

        article_lead = article["lead_paragraph"].strip()

        head, article_lead = article_lead[:19], article_lead[19:]
        text += head

        stops = ["\n", "  ", "\t"]
        for stop in stops:
            article_lead = article_lead.split(stop, 1)[0]

        text += article_lead[: 280 - len(text)]

        return text

    except Exception as e:
        print(e)
