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


def read_jsonl(path, key=None):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    results = []
    for line in lines:
        try:
            raw_json = json.loads(line)
        except json.JSONDecodeError:
            print(f"Error decoding line: {line}")
        if key:
            results.append(raw_json[key])
        else:
            results.append(raw_json)

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
            return user["user_id"]
        except Exception as e:
            if allow_errors:
                print(f"Error creating user: {e}")
                return -1
            else:
                raise e
    else:
        print(f"Would create user: {user.dict()}")
        return 0


def slugify(text):
    return text.lower().replace(" ", "_")


@app.local_entrypoint()
def main(path: str, allow_errors: bool = False, dryrun: bool = True, key=None):
    user_specs = read_jsonl(Path(path), key=key)

    print(f"Creating {len(user_specs)} users...")
    results = []
    for result in create_from_spec.map(
        user_specs, kwargs={"allow_errors": allow_errors, "dryrun": dryrun}
    ):
        results.append(result)
    if not dryrun:
        print(f"Created {len(filter(lambda uid: uid > 0, results))} users.")
    else:
        print(f"Would've created {len(filter(lambda uid: uid == 0, results))} users.")
