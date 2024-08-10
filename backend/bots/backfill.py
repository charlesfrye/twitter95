from datetime import datetime, timedelta

import modal

app = modal.App("user_agent_backfill")


@app.local_entrypoint()
def main(
    start_time: str,
    end_time: str,
    verbose: bool = True,
    dryrun: bool = True,
    delta: int = 10,
):
    post = modal.Function.lookup("user_agent", "go")

    start_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M")
    end_time = datetime.strptime(end_time, "%Y-%m-%d %H:%M")

    datetimes, current_time = [], start_time
    while current_time <= end_time:
        datetimes.append(current_time)
        current_time += timedelta(minutes=delta)

    handles = [
        post.spawn(verbose=verbose, dryrun=dryrun, fake_time=fake_time)
        for fake_time in datetimes
    ]

    for handle in handles:
        handle.get()
