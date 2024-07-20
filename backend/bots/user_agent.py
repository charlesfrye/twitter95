from datetime import datetime
import textwrap
from typing import Optional, Union
import warnings

import modal
from pydantic import BaseModel, Field

import common
from bots.common import Client


image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "openai", "instructor"
)

app = modal.App(
    "user_agent",
    image=image,
    mounts=[common.mount],
)

with image.imports():
    import instructor
    from openai import OpenAI

    import common.pydantic_models as models


class Tweet(BaseModel):
    text: str = Field(..., description="The text content of a tweet")


class QuoteTweet(Tweet):
    quoted: int = Field(..., description="The ID of the tweet being quoted")


class DoNothing(BaseModel):
    nothing: type(None) = Field(None, description="Do nothing")


@app.function(
    image=image,
    secrets=[modal.Secret.from_name("openai-secret")],
    schedule=modal.Period(minutes=10),
)
def go(
    user_name: Optional[int] = None,
    dryrun: bool = False,
    fake_time: Optional[datetime] = None,
    verbose: bool = True,
):
    if user_name is None:
        user_name = get_random_user_name()
    if fake_time is None:
        fake_time = common.to_fake(datetime.utcnow())

    if verbose:
        print(f"running user {user_name} at {fake_time}")
    profile = get_profile(user_name)
    if verbose:
        print(f"user:  {profile.user.display_name}")
    timeline = get_timeline(user_name=user_name, fake_time=fake_time)
    posts = get_posts(user_name=user_name, fake_time=fake_time)
    if verbose:
        print("context retrieved")

    action = take_action(
        profile.user.display_name,
        profile.bio.content,
        timeline,
        posts,
        fake_time=fake_time,
        verbose=verbose,
    )

    print(f"{profile.user.user_name} chose action {type(action)}")
    if verbose:
        if isinstance(action, DoNothing):
            print(f"{profile.user.user_name} did nothing")
        if isinstance(action, Tweet):
            print(f"{profile.user.user_name} twote: {action.text}")
        if isinstance(action, QuoteTweet):
            print(f"{profile.user.user_name} quoted tweet {action.quoted}:")
            for tweet in timeline:
                print(tweet.text) if tweet.tweet_id == action.quoted else None

    if isinstance(action, Tweet):
        if any(tweet.text.strip() == action.text.strip() for tweet in posts):
            warnings.warn("repeating a recent tweet, skipping")
            return
    if isinstance(action, QuoteTweet):
        if any(tweet.text.strip() == action.text.strip() for tweet in timeline):
            warnings.warn("repeating a quote tweet, skipping")
            return
    if isinstance(action, DoNothing) or dryrun:
        return
    else:
        send_tweet(profile.user.user_id, action, fake_time=fake_time)


def send_tweet(user_id, tweet, fake_time=None):
    if fake_time is None:
        fake_time = common.to_fake(datetime.utcnow())

    Client.create_tweet.remote(user_id, fake_time=str(fake_time), **tweet.dict())


def get_profile(user_name="NewYorkTimes"):
    profile = Client.get_user_profile.remote(user_name)

    user = models.ProfileRead(**profile)

    return user


def get_timeline(user_name=None, fake_time=None, limit=10):
    if fake_time is None:
        fake_time = common.to_fake(datetime.utcnow())

    timeline = Client.read_user_timeline.remote(user_name, fake_time, limit)
    timeline = [models.FullTweetRead(**tweet) for tweet in timeline]
    return timeline


def get_posts(user_name=None, fake_time=None, limit=10):
    if fake_time is None:
        fake_time = common.to_fake(datetime.utcnow())

    posts = Client.read_user_posts.remote(user_name, fake_time, limit)
    posts = [models.FullTweetRead(**post) for post in posts]
    return posts


def get_random_user_name():
    query = 'SELECT * FROM "users" WHERE user_id != 3 ORDER BY RANDOM() LIMIT 1;'
    random_user = Client.run_query.remote(query)["result"][0]
    return random_user["user_name"]


def take_action(name, bio, timeline, posts, fake_time=None, verbose=False):
    if fake_time is None:
        fake_time = common.to_fake(datetime.utcnow())

    prompt = f"""
    You are participating in Twitter '95, a simulation of Twitter as it would have been if it had been launched in 1995.

    Your Tweets and activities should maintain kayfabe: tweet exactly as if you were a user at that time.

    The current time in the simulation is {fake_time:%Y-%m-%d %H:%M}.

    You are {name}, a Twitter user with this profile bio:
        ```bio
        {bio}
        ```

    And here are some of your recent Tweets, so you don't repeat yourself:

    ```tweets"""

    prompt = textwrap.dedent(prompt)

    prompt += "\n"
    prompt += "\n".join(
        [
            f"\t```tweet {tweet.tweet_id}\n\t"
            + tweet.text
            + f"\n\t```\n\tposted by you at {tweet.fake_time.isoformat(timespec='minutes')} with TweetID# {tweet.tweet_id}"
            + (f"quoting tweet with TweetID# {tweet.quoted}" if tweet.quoted else "")
            + "\n\t"
            for tweet in posts
        ]
    )
    prompt = textwrap.dedent(prompt)
    prompt += "```"

    prompt += """

    You see this list of Tweets from others on your timeline:
    ```tweets"""

    prompt = textwrap.dedent(prompt)

    prompt += "\n"
    prompt += "\n".join(
        [
            f"\t```tweet {tweet.tweet_id}\n\t"
            + tweet.text
            + f"\n\t```\n\tby @{tweet.author.user_name} at {tweet.fake_time.isoformat(timespec='minutes')} with TweetID# {tweet.tweet_id}"
            + "\n\t"
            for tweet in timeline
        ]
    )
    prompt = textwrap.dedent(prompt)
    prompt += "```"
    prompt += """
    You are participating in the QuoteTweet phase of the simulation. In this phase, you can choose to do one of the following:
        - Write a QuoteTweet in response to a tweet you saw if you think one of them would interest your character.
        - DoNothing, if you think none of the tweets would interest your character.

    Heightened emotions are typical of social media and it's all part of the fun of the simulation.

    This is a simulation, so it is okay to be mean or angry or sad. It's okay to fight or to use foul language.

    Triggering a debate or a discussion is good. It's okay to be controversial. Make sure your character is consistent with the profile you've been given.

    If you choose to write a QuoteTweet:
        - Pick a Tweet you think your character would be interested in. Include the TweetID# in your response.
        - ALWAYS write new content in the voice of your character.
        - NEVER use emojis.
        - NEVER write the content of the Tweet you are quoting. That would be a Retweet, different phase.
        - You may quote your own tweet, not just others'.
        - NEVER quote a tweet you've already quoted.
        - Write a response in the voice and style of your character, maintaining kayfabe.
        - Keep your Tweet short -- 140 characters or less.

    If you choose to DoNothing:
        - Don't worry, you can participate in the next phase of the simulation."""

    prompt = textwrap.dedent(prompt)

    if verbose:
        print(prompt)

    prompt = textwrap.dedent(prompt)

    client = instructor.from_openai(OpenAI())

    action = client.chat.completions.create(
        model="gpt-4o-2024-05-13",
        response_model=Union[QuoteTweet, DoNothing],
        temperature=0.3,
        messages=[{"role": "user", "content": prompt}],
    )

    return action


@app.local_entrypoint()
def main(
    user_name: str = None,
    dryrun: bool = True,
    fake_time: datetime = None,
    verbose: bool = False,
):
    go.remote(user_name, dryrun, fake_time, verbose=verbose)
