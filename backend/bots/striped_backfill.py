"""Script for 'striped' backfilling -- serially across a range of dates and times-of-day and in parallel across specific times."""
from datetime import datetime, timedelta

import modal


app = modal.App("striped-backfill")

MINUTES = 60  # seconds
HOURS = 60 * MINUTES
MAX = 24 * HOURS


@app.local_entrypoint()
def main(
    app_name: str,
    function_name: str,
    start_date: str,
    end_date: str,
    window: int = 10,  # days
    delta: int = 720,  # minutes
    dryrun: bool = True,
):
    print(f"backfilling between {start_date} and {end_date}")
    serial_backfill.remote(
        app_name, function_name, start_date, end_date, window, delta, dryrun
    )


@app.function(timeout=MAX)
def serial_backfill(
    app_name: str,
    function_name: str,
    start_date,
    end_date,
    window: int = 10,
    delta: int = 720,
    dryrun: bool = True,
):
    """Runs several batched backfills in sequence."""
    for window_start, window_end in generate_windows(start_date, end_date, window):
        print(f"running batched backfill between {window_start} and {window_end}")
        batched_backfill.remote(
            app_name,
            function_name,
            window_start,
            window_end,
            delta=delta,
            dryrun=dryrun,
        )


@app.function(timeout=MAX)
def batched_backfill(
    app_name: str,
    function_name: str,
    start_date,
    end_date,
    delta: int = 720,  # 12 hours in minutes!
    dryrun: bool = True,
):
    """Runs a sequence of parallel backfills across chunks separated by a time delta."""
    for start, end in generate_time_pairs(start_date, end_date):
        print(
            f"\trunning a parallel backfill between {start} and {end} separated by {delta} minutes"
        )
        parallel_backfill.remote(
            app_name, function_name, start, end, delta=delta, dryrun=dryrun
        )


@app.function(timeout=MAX)
def parallel_backfill(
    app_name, function_name, start_time, end_time, delta, dryrun, verbose=False
):
    """Runs a backfill in parallel across time chunks of size delta."""
    post = modal.Function.lookup(app_name, function_name)

    start_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M")
    end_time = datetime.strptime(end_time, "%Y-%m-%d %H:%M")

    datetimes, current_time = [], start_time
    while current_time <= end_time:
        datetimes.append(current_time)
        current_time += timedelta(minutes=delta)

    if not dryrun:
        handles = [
            post.spawn(dryrun=dryrun, fake_time=fake_time) for fake_time in datetimes
        ]

        for handle in handles:
            handle.get()
    else:
        if verbose:
            print(
                f"\t\twould backfill {app_name}::{function_name} on {' '.join(str(dt) for dt in datetimes)}"
            )


def generate_time_pairs(start_date, end_date):
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")

    for i in range(72):  # 72 = 6 * 12
        start_time = start_date + timedelta(minutes=10 * i)
        end_time = (
            end_date
            + timedelta(hours=12)
            + timedelta(minutes=10 * i)
            + timedelta(minutes=1)  # in case of exclusive end time
        )

        yield start_time.strftime("%Y-%m-%d %H:%M"), end_time.strftime("%Y-%m-%d %H:%M")


def generate_windows(start_date, end_date, window_length):
    window_start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")

    while (
        window_end_date := window_start_date + timedelta(days=window_length)
    ) < end_date:
        yield (
            window_start_date.strftime("%Y-%m-%d"),
            window_end_date.strftime("%Y-%m-%d"),
        )
        window_start_date = window_end_date + timedelta(days=1)
    yield (
        window_start_date.strftime("%Y-%m-%d"),
        min(window_end_date, end_date).strftime("%Y-%m-%d"),
    )
