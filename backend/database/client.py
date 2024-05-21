from datetime import datetime
from typing import Optional
from uuid import uuid4

import modal

import common

DB_URL_PREFIX = "ex-twitter--db-client-api"
DB_URL_SUFFIX = ".modal.run"

DB_BASE_URL = f"https://{DB_URL_PREFIX}{DB_URL_SUFFIX}"

image = modal.Image.debian_slim(python_version="3.11").pip_install("aiohttp==3.9.5")

app = modal.App(
    "db-client-sdk",
    image=image,
)

with image.imports():
    import aiohttp


@app.cls(mounts=[common.mount])
class Client:
    @modal.enter()
    async def connect(self):
        self.session = aiohttp.ClientSession(base_url=DB_BASE_URL)

    @modal.method()
    async def get_user_by_name(self, user_name):
        async with self.session.get(f"/names/{user_name}/") as resp:
            resp.raise_for_status()
            return await resp.json()

    @modal.method()
    async def get_user_by_id(self, user_id: int):
        async with self.session.get(f"/users/{user_id}/") as resp:
            resp.raise_for_status()
            return await resp.json()

    @modal.method()
    async def create_user(
        self,
        user_name: str,
        display_name: Optional[str] = None,
        profile_pic: Optional[str] = None,
        banner_pic: Optional[str] = None,
    ):
        if display_name is None:
            display_name = user_name

        async with self.session.post(
            "/users/",
            json={
                "user_name": user_name,
                "display_name": display_name,
                "profile_pic": profile_pic,
                "banner_pic": banner_pic,
            },
        ) as resp:
            resp.raise_for_status()
            return await resp.json()

    @modal.method()
    async def delete_user_by_id(self, user_id: int):
        async with self.session.delete(f"/users/{user_id}/") as resp:
            resp.raise_for_status()
            return await resp.json()

    @modal.method()
    async def delete_user_by_name(self, user_name: str):
        async with self.session.get(f"/names/{user_name}/") as resp:
            resp.raise_for_status()
            resp = await resp.json()
            user_id = resp["user_id"]

        async with self.session.delete(f"/users/{user_id}/") as resp:
            resp.raise_for_status()
            return await resp.json()

    @modal.method()
    async def create_tweet(
        self,
        author_id: int,
        text: str,
        real_time: Optional[str] = None,
        fake_time: Optional[str] = None,
        views: Optional[int] = None,
    ):
        async with self.session.post(
            "/tweet/",
            json={
                "author_id": author_id,
                "text": text,
                "real_time": real_time,
                "fake_time": fake_time,
                "views": views,
            },
        ) as resp:
            resp.raise_for_status()
            return await resp.json()

    @modal.method()
    async def delete_tweet(self, tweet_id: int):
        async with self.session.delete(f"/tweet/{tweet_id}/") as resp:
            resp.raise_for_status()
            return await resp.json()

    @modal.method()
    async def read_user_posts(
        self,
        user_id: int,
        fake_time: Optional[datetime] = None,
        limit: int = 10,
        ascending: bool = False,
    ):
        if fake_time is None:
            import common

            fake_time = common.to_fake(datetime.utcnow())
        async with self.session.get(
            "/posts/",
            params={
                "user_id": user_id,
                "fake_time": str(fake_time),
                "limit": limit,
                "ascending": str(ascending).lower(),
            },
        ) as resp:
            resp.raise_for_status()
            return await resp.json()

    @modal.method()
    async def read_user_timeline(
        self,
        user_id: int,
        fake_time: Optional[datetime] = None,
        limit: int = 10,
        ascending: bool = False,
    ):
        if fake_time is None:
            import common

            fake_time = common.to_fake(datetime.utcnow())
        async with self.session.get(
            "/timeline/",
            params={
                "user_id": user_id,
                "fake_time": str(fake_time),
                "limit": limit,
                "ascending": str(ascending).lower(),
            },
        ) as resp:
            resp.raise_for_status()
            return await resp.json()

    @modal.method()
    async def get_user_profile(self, user_id: int):
        async with self.session.get(f"/profile/{user_id}/") as resp:
            resp.raise_for_status()
            return await resp.json()

    @modal.exit()
    async def close(self):
        await self.session.close()


@app.local_entrypoint()
def test(action: str, payload: str = "", expect_fail: bool = False):
    client = Client()
    try:
        if action == "get-user-by-name":
            print(client.get_user_by_name.remote(payload or "NewYorkTimes"))
        elif action == "get-user-by-id":
            print(client.get_user_by_id.remote(payload or 3))
        elif action == "create-user":
            print(client.create_user.remote(payload or str(uuid4())))
        elif action == "delete-user-by-id":
            print(client.delete_user_by_id.remote(int(payload)))
        elif action == "delete-user-by-name":
            print(client.delete_user_by_name.remote(payload))
        elif action == "create-tweet":
            print(client.create_tweet.remote(int(payload), "setting up my twttr"))
        elif action == "read-user-posts":
            print(client.read_user_posts.remote(int(payload)))
        elif action == "read-user-timeline":
            print(client.read_user_timeline.remote(int(payload)))
        elif action == "get-user-profile":
            print(client.get_user_profile.remote(int(payload)))
    except Exception as e:
        if expect_fail:
            print(f"Failure: {e}")
            return
        else:
            raise e
    if expect_fail:
        raise Exception("Expected failure did not occur")
