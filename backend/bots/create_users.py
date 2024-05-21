import json


def read_jsonl(file):
    with open(file, "r", encoding="utf-8") as f:
        for line in f:
            yield json.loads(line)


def load_persona(user_json):
    from . import models

    user = models.User(user_name=slugify(element["name"]), display_name=element["name"])
    session.add(user)
    session.commit()
    bio = models.Bio(user_id=user.user_id, content=element["bio"])
    session.add(bio)
    session.commit()

    return user, bio


def slugify(text):
    return text.lower().replace(" ", "_")
