import json
from pathlib import Path

import modal

import common
from bots.common import Client


image = modal.Image.debian_slim(python_version="3.11").pip_install()

app = modal.App(
    "create-users",
    mounts=[common.mount],
)


def read_jsonl(path):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    results = []
    for line in lines:
        try:
            results.append(json.loads(line))
        except json.JSONDecodeError:
            print(f"Error decoding line: {line}")

    return results


with image.imports():
    import common.pydantic_models as models


@app.function()
def create_from_spec(user_spec, allow_errors=False, dryrun=True):
    user_name = user_spec.get("user_name", slugify(user_spec["name"]))
    display_name = user_spec["name"]
    profile_pic = user_spec.get("profile_pic", None)
    bio = user_spec.get("bio", None)
    if isinstance(bio, str):
        bio = {"content": bio}

    user = models.UserCreate(
        user_name=user_name, display_name=display_name, bio=bio, profile_pic=profile_pic
    )

    if not dryrun:
        try:
            user = Client.create_user.remote(**user.dict())
        except Exception as e:
            if allow_errors:
                print(f"Error creating user: {e}")
                return 0
            else:
                raise e
    else:
        print(f"Would create user: {user.dict()}")
    return 1


def slugify(text):
    return text.lower().replace(" ", "_")


@app.local_entrypoint()
def main(path: str, allow_errors: bool = False, dryrun: bool = True):
    user_specs = read_jsonl(Path(path))

    print(f"Creating {len(user_specs)} users...")
    count = 0
    for result in create_from_spec.map(
        user_specs, kwargs={"allow_errors": allow_errors, "dryrun": dryrun}
    ):
        count += result
    if not dryrun:
        print(f"Created {count} users.")
    else:
        print(f"Would've created {count} users.")
