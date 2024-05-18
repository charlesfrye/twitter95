from datetime import datetime, timedelta


def to_fake(real_time: datetime) -> datetime:
    delta = timedelta(seconds=915_235_088)  # rough number of seconds from 1995 to 2024
    fake_time = real_time - delta
    fake_time = fake_time.replace(tzinfo=None)
    return fake_time
