from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
import warnings

import modal

import common
from bots.common import Client

image = modal.Image.debian_slim(python_version="3.11").pip_install("pynytimes==0.10.0")
volume = modal.Volume.from_name("nyt-headlines", create_if_missing=True)

# TODO: common JSON format for bots
BOT_USER_NAME = "NewYorkTimes"
BOT_DISPLAY_NAME = "New York Times Newspaper"
BOT_PROFILE_PIC = (
    "https://1000logos.net/wp-content/uploads/2017/04/New-York-Times-emblem.jpg"
)
BOT_BANNER_PIC = (
    "https://1000logos.net/wp-content/uploads/2017/04/Font-New-York-Times-Logo.jpg"
)

ARCHIVE_ROOT = Path("/archive")

app = modal.App(
    "nyt_bot",
    secrets=[modal.Secret.from_name("nyt-api-secret")],
    image=image,
    volumes={ARCHIVE_ROOT: volume},
    mounts=[common.mount],
)

with image.imports():
    import json
    import os

    from pynytimes import NYTAPI


@app.function()
def get_or_create_bot_id():
    try:
        bot_user = Client.get_user_by_name.remote(BOT_USER_NAME)
    except Exception:
        bot_user = Client.create_user.remote(
            BOT_USER_NAME, BOT_DISPLAY_NAME, BOT_PROFILE_PIC, BOT_BANNER_PIC
        )
    print(f"bot user: {bot_user}")
    return int(bot_user["user_id"])


@app.function(schedule=modal.Period(days=7))
async def scrape_nyt_archives(month: Optional[datetime] = None):
    nyt_client = connect_nyt()

    if month is None:  # look ahead 10 days
        fake_time = common.to_fake(datetime.utcnow()) + timedelta(days=10)
        month = datetime(fake_time.year, fake_time.month, 1)

    archive = nyt_client.archive_metadata(month)

    print(f"found {len(archive)} entries in the archive for {month:%Y-%m}")
    with open(path_from_date(month), "w") as f:
        f.write(json.dumps(archive))
    volume.commit()

    print(f"saved to {f.name}")

    return archive


def path_from_date(date: datetime):
    return ARCHIVE_ROOT / f"{date:%Y-%m}.json"


def connect_nyt():
    nyt = NYTAPI(os.environ["NYT_API_KEY"], parse_dates=False)
    return nyt


@app.function()
async def post_nyt_articles(
    fake_time: datetime = None, lookahead_hours: int = None, dryrun: bool = False
):
    bot_id = get_or_create_bot_id.local()

    if fake_time is None:
        fake_time = common.to_fake(datetime.utcnow())

    start_hour = fake_time.replace(minute=0, second=0, microsecond=0)
    if lookahead_hours is None:
        lookahead_hours = 1
    lookahead = timedelta(hours=lookahead_hours)

    while fake_time < (start_hour + lookahead):
        articles = get_articles_at_hour(fake_time)
        if articles:
            print(f"posting articles for {fake_time:%Y-%m-%d %H}")
            posted = 0
            for article in articles:
                try:
                    if article := filter_article(article):
                        if text := parse_article(article):
                            if dryrun:
                                print("would have posted", text)
                            else:
                                Client.create_tweet.remote(
                                    author_id=bot_id,
                                    text=text,
                                    fake_time=fake_time.isoformat(),
                                )
                                print("posted", text)
                            posted += 1
                except Exception as e:
                    print(e)
                if posted >= 10:
                    break
            if posted < 10:
                warnings.warn(
                    f"posted only {posted} articles for {fake_time:%Y-%m-%d %H}"
                )
        fake_time += timedelta(hours=1)


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


def filter_article(article):
    try:
        if (
            article["type_of_material"] in ["News", "Op-Ed"]
            and len(article["lead_paragraph"].strip()) >= 20
        ):
            return article
        else:
            print("article not of type News or Op-Ed or lead paragraph too short")
    except Exception as e:
        print(e)


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


@app.local_entrypoint()
def main():
    print(get_or_create_bot_id.remote())
