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

@app.function()
def go(
    dryrun: bool = False,
    fake_time: datetime|None = None,
    verbose: bool = True,
):
    if fake_time is None:
        fake_time = common.to_fake(datetime.utcnow())
    current_fake_time = fake_time
    tweets = Client.read_all_tweets.remote(limit=100)
    if verbose:
        print(f"Read last {len(tweets)} tweets")
    virality = calculate_virality(tweets, current_fake_time)

    # find most viral tweet
    max_viral_tweet = max(virality.items(), key=lambda x: x[1])
    print(f"Most viral tweet: {max_viral_tweet[0]}")
    
    for tweet in tweets:
        if tweet["tweet_id"] == max_viral_tweet[0]:
            if dryrun:
                print(f"would have reposted {tweet['text']}")
            else:
                print(f"oh, a hit tweet:\n{tweet}")

@app.local_entrypoint()
def main(
    dryrun: bool = True,
    fake_time: datetime|None = None,
    verbose: bool = False,
):
    go.remote(dryrun=dryrun, fake_time=fake_time, verbose=verbose)