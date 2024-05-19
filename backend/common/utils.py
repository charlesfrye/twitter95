from datetime import datetime, timedelta

delta = timedelta(seconds=915_235_088)  # rough number of seconds from 1995 to 2024


def to_fake(real_time: datetime) -> datetime:
    fake_time = real_time - delta
    fake_time = fake_time.replace(tzinfo=None)
    return fake_time


def to_real(fake_time: datetime) -> datetime:
    real_time = fake_time + delta
    return real_time
