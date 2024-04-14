import modal
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import Optional
from bson import ObjectId

image = modal.Image.debian_slim().pip_install(
    "pymongo[srv]"
)

stub = modal.Stub("database", image=image, secrets=[modal.Secret.from_name("mongo-secret")])

with image.imports():
    import pymongo

    
# Types
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError('Invalid ObjectId')
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type='string')
        
# class UserId(PyObjectId):
#     @classmethod
#     def __get_pydantic_json_schema__(cls, schema_ref_template: str):
#         return super().__get_pydantic_json_schema__(schema_ref_template)

# class TweetId(PyObjectId):
#     @classmethod
#     def __get_pydantic_json_schema__(cls, schema_ref_template: str):
#         return super().__get_pydantic_json_schema__(schema_ref_template)
    

class TimelineRequest(BaseModel):
    user_id: str
    limit: int = 10

class CreateUserRequest(BaseModel):
    profilePic: str
    bannerPic: str
    username: str
    displayName: str
    # bio: str
    
class CreateTweetRequest(BaseModel):
    author: str
    text: str
    images: Optional[list[str]] = []
    
class ReplyToTweetRequest(BaseModel):
    author: str
    text: str
    root: str # tweet id we are replying to
    
class FollowUserRequest(BaseModel):
    userToBeFollowed: str
    userToFollow: str
     
class Tweet(BaseModel):
    id: PyObjectId
    author: PyObjectId
    text: str
    fakeTime: int
    realTime: int
    views: int = 0
    likes: list[PyObjectId] = [] # user ids
    replies: list[PyObjectId] = [] # tweet Ids
    quoted: Optional[PyObjectId] # If this is a quote tweet, the id of the tweet it is quoating
    retweeted: Optional[PyObjectId] # If this is a retweet, the id of the tweet it is retweeting
    images: Optional[list[str]]
    
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
    def get_mock_timeline(self, user_id, limit=10):
        tweets = mock_feed[:limit]
        return tweets
    
    @modal.method()
    def get_timeline(self, user_id, limit=10):
        tweets = self._get_tweets_from_following(self.db, user_id, limit)
        return tweets

    @modal.method()
    def get_feed(self, user_id, limit=10):
        #todo (find actual mongo implementation details)
        return mock_feed[:limit]

    @modal.method()
    def create_tweet(self, tweet_req: CreateTweetRequest):
        tweet_data = tweet_req.dict()
        tweet_data["author"] = PyObjectId(tweet_data["author"])
        tweet_data["fakeTime"] = 0
        tweet_data["realTime"] = 0
        created_tweet_id = self.db["tweets"].insert_one(tweet_data).inserted_id
        return created_tweet_id
    
    @modal.method()
    def reply_to_tweet(self, reply: ReplyToTweetRequest):
        reply_tweet = reply.dict()
        reply_tweet["author"] = PyObjectId(reply_tweet["author"])
        reply_tweet["root"] = PyObjectId(reply_tweet["root"])
        reply_tweet["fakeTime"] = 0
        reply_tweet["realTime"] = 0
        
        reply_tweet_id = self.db["tweets"].insert_one(reply_tweet).inserted_id
        
        # Add the reply to the original tweet
        self.db["tweets"].update_one({"_id": reply_tweet["root"]}, {"$push": {"replies": reply_tweet_id}})
        
        return reply_tweet_id
    
    @modal.method()
    def get_tweet(self, tweet_id: str):
        requested_tweet = self.client.db["tweets"].find_one({"id": tweet_id})
        return requested_tweet if requested_tweet else {}

    @modal.method()
    def create_user(self, user: CreateUserRequest) -> ObjectId:
        user_data = user.dict()
        user_data["follows"] = []
        created_user_id = self.db["users"].insert_one(user_data).inserted_id
        return created_user_id
    
    @modal.method()
    def follow_user(self, follow_req: FollowUserRequest) -> bool:
        user_to_follow = self.db["users"].find_one({"_id": ObjectId(follow_req.userToFollow)})
        if not user_to_follow:
            return False
        user_to_be_followed = self.db["users"].find_one({"_id": ObjectId(follow_req.userToBeFollowed)})
        if not user_to_be_followed:
            return False
        
        self.db["users"].update_one({"_id": ObjectId(follow_req.userToFollow)}, {"$push": {"follows": ObjectId(follow_req.userToBeFollowed)}})
        return True
    
    @modal.method()
    def get_user(self, user_id: str) -> User:
        user_data = self.db["users"].find_one({"_id": ObjectId(user_id)})
        print(user_data)
        if not user_data:
            return {}
        returned_user = User(
            id=str(user_data["_id"]),
            follows=user_data["follows"],
            profilePic=user_data["profilePic"],
            bannerPic=user_data["bannerPic"],
            username=user_data["username"],
            displayName=user_data["displayName"],
        )
        return returned_user
    
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

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@api.post("/timeline")
async def foo(request: TimelineRequest) -> list[Tweet]:
    client = MongoClient()
    tl = client.get_timeline.local(request.user_id, request.limit)
    return tl

@api.post("/mock_timeline")
async def mock_timeline(request: TimelineRequest) -> list[Tweet]:
    client = MongoClient()
    tl = client.get_mock_timeline.local(request.user_id, request.limit)
    return tl

@api.post("/user")
async def register_user(request: CreateUserRequest) -> PyObjectId:
    client = MongoClient()
    user_id = client.create_user.local(request)
    return str(user_id)

@api.post("/user/follow")
async def follow_user(request: FollowUserRequest) -> bool:
    client = MongoClient()
    return client.follow_user.local(request)

@api.get("/user/{user_id}")
async def get_user(user_id: str) -> User:
    client = MongoClient()
    user = client.get_user.local(user_id)
    return user

@api.post("/tweet")
async def create_tweet(tweet: CreateTweetRequest):
    client = MongoClient()
    return str(client.create_tweet.local(tweet))

@api.post("/tweet/reply")
async def reply_to_tweet(reply: ReplyToTweetRequest):
    client = MongoClient()
    return str(client.reply_to_tweet.local(reply))

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
