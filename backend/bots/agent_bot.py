from datetime import datetime, timezone
from pydantic import BaseModel
import requests
import instructor
from openai import OpenAI

import modal

from backend.common import image

bot_image = image.pip_install("pandas", "requests", "openai", "instructor")

stub = modal.Stub(
    "agent_bot",
    image=bot_image,
)

with bot_image.imports():
    import pandas as pd
    import requests
    import instructor

    from backend import models


class NewTweet(BaseModel):
  text: str

@stub.function(image=bot_image, secrets=[modal.Secret.from_name("openai-secret")])
def go():
    # get the user info for user in question
    for i in range(4, 8):
        userInfo = fetch_user(i)
        # get tweets for user
        tweets_to_read = fetch_timeline(user_id=i, real_time=datetime.utcnow(), limit=10)

        print(userInfo)

        tweet_text = write_new_tweet(userInfo.user.display_name, userInfo.bio.content, tweets_to_read)

        print(f"{userInfo.user.display_name} wrote: {tweet_text}")
        send_tweet(i, tweet_text)
        

def send_tweet(user_id, tweet_text):
        tweet = models.TweetCreate(
            author_id=user_id,
            text=tweet_text,
            fake_time=datetime(1995, 4, 14, 23, 30, 0, 0, timezone.utc),
        )
        print(tweet.json())
        try:
            response = requests.post(
                "https://ex-twitter--db-client-api.modal.run/tweet/", data=tweet.json()
            )
            response.raise_for_status()
        except Exception as e:
            print(f"error posting tweet {tweet}")
            print(e)


def fetch_user(user_id=0):
    try:
        params = {"user_id": user_id}
        response = requests.post(
            f"https://ex-twitter--db-client-api.modal.run/profile", params=params
        )
        response.raise_for_status()
        data = response.json()
        if data is None:
            print(f"User {user_id} not found. Returning None...")
            return None
        else:
            user = models.ProfileRead(**data)
            return user
    except requests.exceptions.HTTPError as e:
        print(e)
        raise
    
def fetch_timeline(user_id=None, real_time=datetime.utcnow(), limit=10):
    try:
        params = {"user_id": user_id, "real_time": real_time, "limit": limit}
        response = requests.post(
            "https://ex-twitter--db-client-api.modal.run/timeline/", params=params
        )
        response.raise_for_status()
        data = response.json()
        if data is None:
            print(f"Timeline for user {user_id} not found. Returning None...")
            return None
        else:
            timeline = [models.TweetRead(**tweet) for tweet in data]
            return timeline
    except requests.exceptions.HTTPError as e:
        print(e)
        raise

def write_new_tweet(name, bio, tweet_stream):
  new_tweet_prompt = f"You are {name}, a Twitter user with this profile bio: {bio}. You see this list of Tweets: {tweet_stream}. Write a new original Tweet in your style, responding to a specific news item from the list. Do NOT use emojis."
  client = instructor.from_openai(OpenAI())

  new_tweet = client.chat.completions.create(
    model="gpt-3.5-turbo",
    response_model=NewTweet,
    messages=[{"role": "user", "content": new_tweet_prompt}]
  )
  return new_tweet.text


@stub.local_entrypoint()
def main():
    go.remote()
