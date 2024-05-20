from datetime import datetime
from typing import Optional

import modal
from pydantic import BaseModel

import common
from bots.common import Client


# TODO: replace once we no longer use the models?
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "asyncpg==0.29.0", "sqlalchemy[asyncio]==2.0.30"
)

image = image.pip_install("pandas", "requests", "openai", "instructor")

app = modal.App(
    "user_agent",
    image=image,
    mounts=[common.mount],
)

with image.imports():
    import instructor
    from openai import OpenAI
    import requests

    import common.pydantic_models as models


class NewTweet(BaseModel):
    text: Optional[str]


@app.function(image=image, secrets=[modal.Secret.from_name("openai-secret")])
def go(
    user_id: Optional[int] = None,
    dryrun: bool = False,
    fake_time: Optional[datetime] = None,
):
    if user_id is None:
        user_id = 4
    if fake_time is None:
        fake_time = common.to_fake(datetime.utcnow())

    # TODO: switch to Client
    userInfo = fetch_user(user_id)
    # TODO: switch to Client
    tweets_to_read = fetch_timeline(user_id=user_id, fake_time=fake_time)

    tweet_text = write_new_tweet(
        userInfo.user.display_name, userInfo.bio.content, tweets_to_read
    )

    print(f"{userInfo.user.display_name} twote: {tweet_text}")
    if not dryrun:
        # TODO: switch to Client
        send_tweet(user_id, tweet_text, fake_time=fake_time)


def send_tweet(user_id, tweet_text, fake_time=None):
    if fake_time is None:
        fake_time = common.to_fake(datetime.utcnow())
    tweet = models.TweetCreate(
        author_id=user_id,
        text=tweet_text,
        fake_time=fake_time,
    )
    response = requests.post(
        "https://ex-twitter--db-client-api-dev.modal.run/tweet/", data=tweet.json()
    )
    response.raise_for_status()


def fetch_user(user_id=0):
    params = {"user_id": user_id}
    response = requests.post(
        "https://ex-twitter--db-client-api-dev.modal.run/profile/", params=params
    )
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"User {user_id} not found.")
        print(f"Error: {e}")
        return None
    else:
        user = models.ProfileRead(**response.json())
        return user


def fetch_timeline(user_id=None, fake_time=None, limit=10):
    if fake_time is None:
        fake_time = common.to_fake(datetime.utcnow())
    params = {"user_id": user_id, "fake_time": fake_time, "limit": limit}
    response = requests.get(
        "https://ex-twitter--db-client-api-dev.modal.run/timeline/", params=params
    )
    response.raise_for_status()
    data = response.json()
    if data is None:
        print(f"Timeline for user {user_id} not found. Returning None...")
        return None
    else:
        timeline = [models.TweetRead(**tweet) for tweet in data]
        return timeline


def write_new_tweet(name, bio, tweet_stream, fake_time=None):
    if fake_time is None:
        fake_time = common.to_fake(datetime.utcnow())

    # TODO: dedent
    new_tweet_prompt = f"""You are participating in Twitter '95, a simulation of Twitter as it would have been if it had been launched in 1995.

Your Tweets and activities should maintain kayfabe: tweet exactly as if you were a user at that time.

The current time in the simulation is {fake_time:%Y-%m-%d %H:%M}.

You are {name}, a Twitter user with this profile bio:
```bio
{bio}
```

You see this list of Tweets:
```tweets
"""
    new_tweet_prompt += "\n".join(
        [
            "```tweet\n" + f"{tweet.text} at {tweet.fake_time.isoformat()}" + "\n```"
            for tweet in tweet_stream
        ]
    )
    new_tweet_prompt += """
```

You may now decide what to next:
- Write a Tweet in response to a Tweet you saw. Pick a Tweet you think the user would be interested in.
- Write your own Tweet.
- Do nothing, if you don't think your character would have anything to say right now.

If you choose to write a Tweet:
- Do NOT use emojis."""

    client = instructor.from_openai(OpenAI())

    new_tweet = client.chat.completions.create(
        model="gpt-4o-2024-05-13",
        response_model=NewTweet,
        temperature=0.3,
        messages=[{"role": "user", "content": new_tweet_prompt}],
    )
    return new_tweet.text


@app.local_entrypoint()
def main(user_id: int = None, dryrun: bool = True):
    go.remote(user_id, dryrun)
