from datetime import datetime, timedelta
import warnings

import modal

import common
import bots.common
from . import common as nyt_common
from .common import app


BOT_USER_NAME = "NewYorkTimes"
BOT_DISPLAY_NAME = "New York Times Newspaper"


@app.function(schedule=modal.Period(hours=1))
async def post_nyt_articles(
    fake_time: datetime = None, lookahead_hours: int = None, dryrun: bool = False
):
    bot_id = nyt_common.get_or_create_bot_id.local(
        user_name=BOT_USER_NAME,
        display_name=BOT_DISPLAY_NAME,
        profile_pic=nyt_common.BOT_PROFILE_PIC,
    )

    if fake_time is None:
        fake_time = common.to_fake(datetime.utcnow())

    start_hour = fake_time.replace(minute=0, second=0, microsecond=0)
    if lookahead_hours is None:
        lookahead_hours = 1
    lookahead = timedelta(hours=lookahead_hours)

    while fake_time < (start_hour + lookahead):
        articles = nyt_common.get_articles_at_hour(fake_time)
        if articles:
            print(f"posting articles for {fake_time:%Y-%m-%d %H}")
            posted = 0
            for article in articles:
                try:
                    if article := filter_article(article):
                        if text := nyt_common.parse_article(article):
                            if dryrun:
                                print("would have posted", text)
                            else:
                                bots.common.Client.create_tweet.remote(
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


def filter_article(article):
    try:
        if (
            article["type_of_material"] in ["News", "Op-Ed"]
            and len(article["lead_paragraph"].strip()) >= 20
        ):
            if "was married" not in article["lead_paragraph"]:
                return article
        else:
            print("article not of type News or Op-Ed or lead paragraph too short")
    except Exception as e:
        print(e)


@app.local_entrypoint()
def main(fake_time: str = None, lookahead_hours: int = None):
    nyt_common.get_or_create_bot_id.remote(user_name=BOT_USER_NAME)
