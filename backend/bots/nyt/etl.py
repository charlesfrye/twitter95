from datetime import datetime, timedelta
import os
from typing import Optional

import modal

import common
from . import common as nyt_common


app = modal.App(
    "nyt_etl",
    image=modal.Image.debian_slim(python_version="3.11").pip_install(
        "pynytimes==0.10.0"
    ),
    secrets=[modal.Secret.from_name("nyt-api-secret")],
    volumes=nyt_common.volumes,
    mounts=[common.mount],
)

with nyt_common.image.imports():
    import json

    from pynytimes import NYTAPI


def connect_nyt():
    nyt = NYTAPI(os.environ["NYT_API_KEY"], parse_dates=False)
    return nyt


@app.function(schedule=modal.Period(days=7))
async def scrape_nyt_archives(month: Optional[datetime] = None):
    nyt_client = connect_nyt()

    if month is None:  # look ahead 10 days
        fake_time = common.to_fake(datetime.utcnow()) + timedelta(days=10)
        month = datetime(fake_time.year, fake_time.month, 1)

    archive = nyt_client.archive_metadata(month)

    print(f"found {len(archive)} entries in the archive for {month:%Y-%m}")
    with open(nyt_common.path_from_date(month), "w") as f:
        f.write(json.dumps(archive))
    nyt_common.volume.commit()

    print(f"saved to {f.name}")

    return archive


@app.local_entrypoint()
def main():
    scrape_nyt_archives.remote()
