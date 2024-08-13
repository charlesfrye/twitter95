from datetime import datetime, timedelta
import re
import os
import modal

delta = timedelta(seconds=915_235_088)  # rough number of seconds from 1995 to 2024


def to_fake(real_time: datetime) -> datetime:
    fake_time = real_time - delta
    fake_time = fake_time.replace(tzinfo=None)
    return fake_time


def to_real(fake_time: datetime) -> datetime:
    real_time = fake_time + delta
    return real_time


def extract_hashtags(text):
    hashtag_pattern = (
        r"#\w+"  # starts with a #, then any number of letters, digits, or underscores
    )
    hashtags = set(re.findall(hashtag_pattern, text))
    return hashtags


screenshot_cache = modal.Dict.from_name("screnshot-cache", create_if_missing=True)


def screenshot_tweet(tweet_id):
    import requests

    # Take screenshot or use cached screenshot
    image_cache_id = f"{tweet_id}.jpg"
    image_bytes = screenshot_cache.get(image_cache_id)
    if image_bytes is None:
        print("No image cache found, fetching from screenshotone")
        api_key = os.getenv("SCREENSHOTONE_API_KEY")
        delay = 5 # time to allow for the page to populate its data
        screenshot_url = f"https://api.screenshotone.com/take?access_key={api_key}&url=https%3A%2F%2Fwww.twitter-95.com%2Ftweet%2F{tweet_id}%3Frender_as_og%3Dtrue&full_page=false&viewport_width=800&viewport_height=450&device_scale_factor=3&format=jpg&image_quality=80&block_ads=true&block_cookie_banners=true&block_banners_by_heuristics=false&block_trackers=true&delay={delay}&timeout=60"
        response = requests.get(screenshot_url)
        if response.status_code == 200:
            image_bytes = response.content
            screenshot_cache[image_cache_id] = image_bytes
        else:
            raise Exception(f"Error fetching image: {response.status_code}")
    else:
        print("Image cache found, not fetching from screenshotone")

    return image_bytes
