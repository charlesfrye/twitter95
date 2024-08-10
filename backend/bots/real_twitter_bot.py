from datetime import datetime
import math

import modal

import common
from bots.common import Client
from bots.real_twitter.client import post_to_real_twitter


image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "aiohttp==3.9.5", "requests==2.32.3", "tweepy==4.14.0"
)

app = modal.App(
    "repost-bot",
    image=image,
    secrets=[
        modal.Secret.from_name("twitter-api"),
        modal.Secret.from_name("screenshotone-api"),
    ],
)


def calculate_virality(tweets, current_fake_time, decay_factor=0.05):
    """ "
    Calculates the virality score for each tweet in the list of tweets.

    decay_factor: how much we decay the weight of each quoted tweet per hour since it was quoted.
    """
    virality_scores = {}

    # for each referenced tweet, get list of times it was quoted
    quote_times = {}
    for tweet in tweets:
        tweet_id = tweet["quoted"]
        if tweet_id is None:
            # skip tweets that don't have a quoted tweet
            continue
        if tweet_id not in quote_times:
            quote_times[tweet_id] = []

        tweet_datetime = datetime.fromisoformat(tweet["fake_time"])
        quote_times[tweet_id].append(tweet_datetime)

    # look at those times and calculate the virality score
    for tweet_id, fake_times in quote_times.items():
        # the more times it was quoted, the higher the score
        score = 0
        for fake_time in fake_times:
            # the more recent the time, the higher we weight it in the score
            time_diff = (
                current_fake_time - fake_time
            ).total_seconds() / 3600  # hours since
            weight = math.exp(
                -decay_factor * time_diff
            )  # the higher the diff, the lower the weight
            score += weight

        virality_scores[tweet_id] = score

    # Normalize scores to make them more comparable
    max_score = max(virality_scores.values(), default=0)
    if max_score > 0:
        for tweet_id in virality_scores:
            virality_scores[tweet_id] /= max_score

    return virality_scores


tweet_cache = modal.Dict.from_name("repost-bot-tweet-log", create_if_missing=True)


@app.function(
    schedule=modal.Period(minutes=60),
)
def go(
    dryrun: bool = False,
    fake_time: datetime | None = None,
):
    if fake_time is None:
        # list exports on common module
        fake_time = common.to_fake(datetime.utcnow())
    current_fake_time = fake_time

    tweets = Client.read_all_tweets.remote(limit=500)

    print(f"Read last {len(tweets)} tweets")
    virality = calculate_virality(tweets, current_fake_time)

    # ok supermaven ai model, implement this
    def get_tweet_by_id(tweet_id, tweets):
        for tweet in tweets:
            if tweet["tweet_id"] == tweet_id:
                return tweet
        return None

    # sort by virality score
    virality = sorted(virality.items(), key=lambda x: x[1], reverse=True)

    viral_tweet = {}
    viral_tweet_id = {}
    for tweet_id, _ in virality:
        quoted_tweet = get_tweet_by_id(tweet_id, tweets)
        if quoted_tweet is None:
            # tweet doesn't exist in our limited scan of tweets
            continue

        if quoted_tweet["quoted"] is None:
            # quoted_tweet is not a quote itself, meaning it's from a news source and not a personality
            continue

        viral_tweet = quoted_tweet
        viral_tweet_id = tweet_id
        break

    print("Found most viral tweet:", viral_tweet)
    author = Client.get_user_by_id.remote(viral_tweet["author_id"])

    if viral_tweet_id in tweet_cache:
        print(f"Already reposted. Skipping.")
        return

    if dryrun:
        print(f"Would have reposted the following tweet:\n{viral_tweet['text']}")
    else:
        image_bytes = common.screenshot_tweet(viral_tweet_id)
        post_to_real_twitter(viral_tweet, author, image_bytes)
        tweet_cache[viral_tweet_id] = True


@app.local_entrypoint()
def main(
    dryrun: bool = True,
    fake_time: datetime | None = None,
):
    go.remote(dryrun=dryrun, fake_time=fake_time)
