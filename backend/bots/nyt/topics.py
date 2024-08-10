from datetime import datetime, timedelta
import json
from pathlib import Path
import random
import warnings

import modal

import common
import bots.common
from . import common as nyt_common


BOT_DATA_FILE = Path(__file__).parent.parent / "data" / "nyt-topics.jsonl"

app = modal.App(
    "nyt-topics",
    image=modal.Image.debian_slim(python_version="3.11"),
    mounts=[modal.Mount.from_local_file(BOT_DATA_FILE)],
)
app.include(nyt_common.app)


@app.function(
    schedule=modal.Period(hours=1), volumes=nyt_common.volumes, image=nyt_common.image
)
async def post_nyt_articles(
    fake_time: datetime = None,
    lookahead_hours: int = None,
    dryrun: bool = False,
    topics_bot_name: str | None = None,
):
    topics_bot = read_topics_bot(topics_bot_name)
    bot_id = nyt_common.get_bot_id.local(topics_bot["user"]["user_name"])

    if fake_time is None:
        fake_time = common.to_fake(datetime.utcnow())

    start_hour = fake_time.replace(minute=0, second=0, microsecond=0)
    if lookahead_hours is None:
        lookahead_hours = 1
    lookahead = timedelta(hours=lookahead_hours)

    while fake_time < (start_hour + lookahead):
        articles = nyt_common.get_articles_at_hour(fake_time, sort=True)
        if len(articles):
            print(f"posting articles for {fake_time:%Y-%m-%d %H}")
            posted = 0
            for article in articles:
                try:
                    if accept_article(article, topics_bot["desks"]):
                        if text := nyt_common.parse_article(article):
                            if dryrun:
                                print("would have posted", text)
                            else:
                                bots.common.Client.create_tweet.remote(
                                    author_id=bot_id,
                                    text=text,
                                    fake_time=(
                                        fake_time
                                        + timedelta(
                                            hours=12
                                        )  # offset topics bots from frontpage by 12 hours
                                    ).isoformat(),
                                )
                                print("posted", text)
                            posted += 1
                except Exception as e:
                    print(e)
                if posted >= 10:
                    break
            if posted < 5:
                warnings.warn(
                    f"{topics_bot['user']['user_name']} posted only {posted} articles for {fake_time:%Y-%m-%d %H}"
                )
        fake_time += timedelta(hours=1)


@app.function(schedule=modal.Period(hours=1))
def post_all_bots(fake_time: datetime = None, dryrun: bool = False):
    topics_bots = get_topics_bots()
    for topic_bot in topics_bots:
        post_nyt_articles.remote(
            topics_bot_name=topic_bot["user"]["user_name"],
            dryrun=dryrun,
            fake_time=fake_time,
        )


def accept_article(article, topic_desks):
    try:
        if (
            article["type_of_material"] in ["News", "Op-Ed"]  # news-worthy
            and len(article["lead_paragraph"].strip()) >= 20
            and match_desks(article["news_desk"], topic_desks)
            and not (
                article["print_section"] == "A" and article["print_page"] in [1, "1"]
            )  # reduce overlap with frontpage bot
        ):
            if article["headline"]["main"].strip().upper() != "NO HEADLINE":
                return True
    except Exception as e:
        print(e)


def match_desks(article_desk, topic_desks):
    if article_desk.lower().strip() in map(str.lower, topic_desks):
        return True


def read_topics_bot(topics_bot_name: str | None = None):
    topics_bots = get_topics_bots()
    if topics_bot_name is None:
        return random.choice(topics_bots)
    else:
        try:
            return next(
                (
                    bot
                    for bot in topics_bots
                    if bot["user"]["user_name"] == topics_bot_name
                )
            )
        except StopIteration:
            raise ValueError(f"Bot {topics_bot_name} not found in {BOT_DATA_FILE}")


def get_topics_bots():
    with open(BOT_DATA_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    return [json.loads(line) for line in lines]


@app.local_entrypoint()
def main(fake_time: str = None, lookahead_hours: int = None, dryrun: bool = True):
    post_nyt_articles.remote(fake_time, lookahead_hours, dryrun=dryrun)
