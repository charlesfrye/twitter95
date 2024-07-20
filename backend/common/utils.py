from datetime import datetime, timedelta
import re

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
