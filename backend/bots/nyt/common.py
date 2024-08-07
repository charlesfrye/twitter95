"""Shared configuration and behavior for NYT bots."""
import modal

import common
from bots.common import Client

from datetime import datetime
from pathlib import Path

BOT_PROFILE_PIC = (
    "https://1000logos.net/wp-content/uploads/2017/04/New-York-Times-emblem.jpg"
)

image = modal.Image.debian_slim(python_version="3.11").pip_install("pandas==2.2.2")
volume = modal.Volume.from_name("nyt-headlines", create_if_missing=True)
ARCHIVE_ROOT = Path("/archive")

volumes = {ARCHIVE_ROOT: volume}

URL_DISPLAY_LEN = 33 + len("...")  # size of URLs when rendered in frontend

with image.imports():
    import json

    import pandas as pd


app = modal.App(
    "nyt_bot",
    image=image,
    volumes={ARCHIVE_ROOT: volume},
    mounts=[common.mount],
)


@app.function()
def get_bot_id(user_name: str):
    bot_user = Client.get_user_by_name.remote(user_name)
    bot_user_id = bot_user["user_id"]
    print(f"bot user: {bot_user}")
    return int(bot_user_id)


def get_articles_at_hour(hour: datetime, sort=False):
    hour = hour.replace(minute=0, second=0, microsecond=0)
    archive = load_archive(path_from_date(hour), sort=sort)
    articles = []
    for _idx, article in archive.iterrows():
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
                articles.append(article)
        except KeyError:
            continue
    print(f"found {len(articles)} articles for {hour:%Y-%m-%d %H}")
    return articles


def parse_article(article):
    try:
        text = ""

        try:
            head = article["headline"]["main"].strip()
            head = " ".join(head.split("\n"))
            text += head + "\n"
        except KeyError:
            pass

        article_lead = article["lead_paragraph"].strip()
        text += article_lead[:19]
        article_lead = article_lead[19:]

        stops = ["\n", "  ", "\t"]
        for stop in stops:
            article_lead = article_lead.split(stop, 1)[0]

        if article["web_url"]:
            url = article["web_url"]

        text += article_lead[: 280 - len(text) - URL_DISPLAY_LEN]
        text += f" {url}"

        return text

    except Exception as e:
        print(e)


def path_from_date(date: datetime):
    return ARCHIVE_ROOT / f"{date:%Y-%m}.json"


def read_archive(filename):
    contents = Path(filename).read_text()
    return json.loads(contents)


def load_archive(filename, sort=False):
    archive = read_archive(filename)
    df = pd.DataFrame.from_records(archive)
    df["print_section"] = df["print_section"].map(
        lambda elem: elem if not pd.isna(elem) else ""
    )
    if sort:
        df = sort_importance(df)
    return df


def section_sort_key(section):
    if isinstance(section, str):
        if section.isalpha():
            return (0, section)  # Letters come first
        elif section.isdigit():
            return (1, int(section))  # Numbers come second, sorted numerically
        else:
            return (2, section)  # Any other format comes last
    else:
        return (3, str(section))  # Handle non-string types


def try_int(x):
    try:
        return int(x)
    except ValueError:
        return int(1e6)


def sort_importance(df):
    return df.sort_values(
        by=["print_section", "print_page"],
        key=lambda col: col.map(section_sort_key)
        if col.name == "print_section"
        else col.astype(str).map(lambda x: try_int(x)),
    )
