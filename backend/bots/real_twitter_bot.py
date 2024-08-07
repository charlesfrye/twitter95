import modal
import common
from bots.common import Client
from datetime import datetime
import math

image = modal.Image.debian_slim(python_version="3.11").pip_install("aiohttp==3.9.5")

app = modal.App(
    "repost-bot",
    image=image
)

from datetime import datetime
import math

def calculate_virality(tweets, current_fake_time, decay_factor=0.05):
    """"
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
            time_diff = (current_fake_time - fake_time).total_seconds() / 3600 # hours since
            weight = math.exp(-decay_factor * time_diff) # the higher the diff, the lower the weight
            score += weight

        virality_scores[tweet_id] = score

    # Normalize scores to make them more comparable
    max_score = max(virality_scores.values(), default=0)
    if max_score > 0:
        for tweet_id in virality_scores:
            virality_scores[tweet_id] /= max_score

    return virality_scores

prev_tweets = modal.Dict.from_name("repost-bot-tweet-log", create_if_missing=True)

@app.function(
    schedule=modal.Period(minutes=60),
)
def go(
    dryrun: bool = False,
    fake_time: datetime|None = None,
    verbose: bool = True,
):
    if fake_time is None:
        # list exports on common module
        fake_time = common.to_fake(datetime.utcnow())
    current_fake_time = fake_time
    tweets = Client.read_all_tweets.remote(limit=500)
    if verbose:
        print(f"Read last {len(tweets)} tweets")
    virality = calculate_virality(tweets, current_fake_time)


    # todo this code is fucked
    # for all virality scores, we want to find the "parent" tweet
    # we want to find the highest virality score tweet where the parent tweet is also a quote
    # that parent tweet may not exist in our limited scan of tweets

    # ok supermaven ai model, implement this
    def get_tweet_by_id(tweet_id, tweets):
        for tweet in tweets:
            if tweet["tweet_id"] == tweet_id:
                return tweet
        return None

    # sort by virality score
    virality = sorted(virality.items(), key=lambda x: x[1], reverse=True)

    viral_tweet = None
    viral_tweet_id = None
    for tweet_id, virality_score in virality:
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

    if viral_tweet_id in prev_tweets:
        print(f"Already reposted. Skipping.")
        return
    if dryrun:
        print(f"would have reposted the following tweet:\n{viral_tweet['text']}")
    else:
        repost_tweet(viral_tweet_id, viral_tweet, dryrun, verbose)

def repost_tweet(tweet_id, tweet, dryrun, verbose):
    print(f"oh, a hit tweet:\n{tweet}")


@app.local_entrypoint()
def main(
    dryrun: bool = True,
    fake_time: datetime|None = None,
    verbose: bool = True,
):
    go.remote(dryrun=dryrun, fake_time=fake_time, verbose=verbose)