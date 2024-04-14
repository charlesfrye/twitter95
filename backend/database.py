import modal
from fastapi import FastAPI, CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

image = modal.Image.debian_slim().pip_install(
    "pymongo[srv]"
)

stub = modal.Stub("database", image=image, secrets=[modal.Secret.from_name("mongo-secret")])

with image.imports():
    import pymongo

# Types
class TimelineRequest(BaseModel):
    user_id: int
    limit: int = 10

class CreateUserRequest(BaseModel):
    profilePic: str
    bannerPic: str
    username: str
    displayName: str
    # bio: str

class Tweet(BaseModel):
    id: int
    text: str

class User(BaseModel):
    id: str
    follows: list[int]
    profilePic: str
    bannerPic: str
    username: str
    displayName: str


@stub.cls(
    concurrency_limit=10,
)
class MongoClient:
    def __init__(self, user=None, password=None, uri=None) -> None:
        import os
        import urllib
        mongodb_user = user or os.environ["MONGODB_USER"]
        mongodb_user = urllib.parse.quote_plus(mongodb_user)
        mongodb_password = password or os.environ["MONGODB_PASSWORD"]
        mongodb_password = urllib.parse.quote_plus(mongodb_password)
        mongodb_host = uri or os.environ["MONGODB_HOST"]
        connection_string = f"mongodb+srv://{mongodb_user}:{mongodb_password}@{mongodb_host}/?retryWrites=true&w=majority"

        self.client = pymongo.MongoClient(connection_string, connect=True, appname="ex-twitter")
        self.db = self.client["ex-twitter"]

    @modal.exit()
    def close(self):
        self.client.close()

    @modal.method()
    def check_connection(self):
        return self.client.server_info()

    @modal.method()
    def get_timeline(self, user_id, limit=10):
        # tweets = self._get_tweets_from_following(user_id, limit)
        tweets = mock_feed[:limit]
        return tweets

    @modal.method()
    def get_feed(self, user_id, limit=10):
        #todo (find actual mongo implementation details)
        return mock_feed[:limit]

    @modal.method()
    def get_user(self, user_id):
        #todo (find actual mongo implementation details)
        return {"id": 1, "name": "Alice"}

    @modal.method()
    def create_tweet(self, tweet: Tweet):
        #todo (find actual mongo implementation details)
        return tweet

    @modal.method()
    def get_tweet(self, tweet_id: str):
        requested_tweet = self.client.db["tweets"].find_one({"id": tweet_id})
        return requested_tweet if requested_tweet else {}

    @modal.method()
    def create_user(self, user: CreateUserRequest):
        user_data = user.dict()
        user_data["follows"] = []
        created_user = self.db["users"].insert_one(user_data)
        return created_user

    @modal.method()
    def like_tweet(self, tweet_id, user_id):
        #todo (find actual mongo implementation details)
        return True

    def _get_user_following(db, user_id):
        """returns the list of users the user follows"""
        user_data = db["users"].find_one({"id": user_id})
        return user_data.get('follows', []) if user_data else []

    def _get_tweets_from_following(self, db, user_id, limit=10):
        follows = self._get_user_following(user_id)
        tweets_collection = db["tweets"]
        tweets = list(tweets_collection.find({"author": {"$in": follows}}).sort("fakeTime", pymongo.DESCENDING).limit(limit))
        return tweets

api = FastAPI()

origins = [
    "",
]

api.add_middleware(
    CORSMiddleware,
    allow_origin_regex=["https://.*\.vercel\.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@api.post("/timeline")
async def foo(request: TimelineRequest) -> list[Tweet]:
    client = MongoClient()
    tl = client.get_timeline.local(request.user_id, request.limit)
    return tl

@api.post("/user")
async def register_user(request: CreateUserRequest) -> User:
    client = MongoClient()
    user = client.create_user.local(request)

    return user

@api.get("/bar")
async def bar(arg="world"):
    client = MongoClient()
    return HTMLResponse(f"<h1>Hello Fast {client.test}!</h1>")

@api.get("/tweet/{tweet_id}")
async def get_tweet(tweet_id: str):
    client = MongoClient()
    tweet = client.get_tweet.local(tweet_id)
    return tweet


@stub.function(image=image)
@modal.asgi_app()
def fastapi_app():
    return api


# Mock data
mock_feed = [
    {
        "id": "1",
        "text": "Hello, world!",
        "images": [],
        "author": "1",
        "replies": ["2"],
        "root": "1",
        "quoted": None,
        "retweeted": None,
        "likedBy": [],
        "fakeTime": 0,
        "realTime": 0,
        "views": 0,
    },
    {
        "id": "2",
        "text": "This is a reply to tweet 1",
        "images": [],
        "author": "2",
        "replies": [],
        "root": "1",
        "quoted": None,
        "retweeted": None,
        "likedBy": [],
        "fakeTime": 1,
        "realTime": 1,
        "views": 0,
    },
    {
        "id": "3",
        "text": "This is a tweet with an image",
        "images": [
            "https://fastly.picsum.photos/id/630/200/300.jpg?hmac=Qat1qmS4S2t4rLYqAEW2wwkzkXdCnsYltDyo8kbmjfw"
        ],
        "author": "1",
        "replies": [],
        "root": "3",
        "quoted": None,
        "retweeted": None,
        "likedBy": [],
        "fakeTime": 2,
        "realTime": 2,
        "views": 0,
    },
    {
        "id": "4",
        "text": "This is a tweet with a quoted tweet",
        "images": [],
        "author": "2",
        "replies": [],
        "root": "4",
        "quoted": "3",
        "retweeted": None,
        "likedBy": [],
        "fakeTime": 3,
        "realTime": 3,
        "views": 0,
    },
    {
        "id": "5",
        "text": "This is a tweet with a retweet",
        "images": [],
        "author": "1",
        "replies": [],
        "root": "5",
        "quoted": None,
        "retweeted": "4",
        "likedBy": [],
        "fakeTime": 4,
    },
]
