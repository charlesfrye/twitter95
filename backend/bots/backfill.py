from datetime import datetime, timedelta

import modal

app = modal.App("backfill")


@app.local_entrypoint()
def main(
    app_name: str,
    function_name: str,
    start_time: str,
    end_time: str,
    dryrun: bool = True,
    delta: int = 10,
):
    post = modal.Function.lookup(app_name, function_name)

    start_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M")
    end_time = datetime.strptime(end_time, "%Y-%m-%d %H:%M")

    datetimes, current_time = [], start_time
    while current_time <= end_time:
        datetimes.append(current_time)
        current_time += timedelta(minutes=delta)

    handles = [
        post.spawn(dryrun=dryrun, fake_time=fake_time) for fake_time in datetimes
    ]

    for handle in handles:
        handle.get()
