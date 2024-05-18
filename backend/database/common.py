from datetime import datetime, timedelta

import modal

image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "asyncpg==0.29.0", "sqlalchemy[asyncio]==2.0.30"
)


def to_fake(real_time: datetime) -> datetime:
    delta = timedelta(seconds=915_235_088)  # rough number of seconds from 1995 to 2024
    fake_time = real_time - delta
    fake_time = fake_time.replace(tzinfo=None)
    return fake_time
