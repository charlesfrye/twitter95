import modal
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

image = modal.Image.debian_slim().pip_install(
    "pymongo"
)

stub = modal.Stub("database", image=image)

with image.imports():
    import pymongo
    
# Types
class TimelineRequest(BaseModel):
    user_id: int
    limit: int = 10
    
class Tweet(BaseModel):
    id: int
    text: str

@stub.cls(
    concurrency_limit=10,
)
class MongoClient:
    @modal.enter()
    def connect(self):
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")
        return self.client
    
    @modal.exit()
    def close(self):
        self.client.close()
        
    @modal.method()
    def check_connection(self):
        return self.client.server_info()
    
    @modal.method()
    def get_timeline(self, user_id, limit=10):
        #todo (find actual mongo implementation details)
        return mock_feed[:limit]
 
api = FastAPI()

@api.post("/timeline")
async def foo(request: TimelineRequest) -> list[Tweet]:
    client = MongoClient()
    tl = client.get_timeline.local(request.user_id, request.limit)
    return tl


@api.get("/bar")
async def bar(arg="world"):
    return HTMLResponse(f"<h1>Hello Fast {arg}!</h1>")


@stub.function(image=image)
@modal.asgi_app()
def fastapi_app():
    return api



# Mock data
mock_feed = [
    {
        "id": 1,
        "text": "Hello, world!",
        "images": [],
        "author": 1,
        "replies": [2],
        "root": 1,
        "quoted": None,
        "retweeted": None,
        "likedBy": [],
        "fakeTime": 0,
        "realTime": 0,
        "views": 0
    },
    {
        "id": 2,
        "text": "This is a reply to tweet 1",
        "images": [],
        "author": 2,
        "replies": [],
        "root": 1,
        "quoted": None,
        "retweeted": None,
        "likedBy": [],
        "fakeTime": 1,
        "realTime": 1,
        "views": 0
    },
    {
        "id": 3,
        "text": "This is a tweet with an image",
        "images": ["https://fastly.picsum.photos/id/630/200/300.jpg?hmac=Qat1qmS4S2t4rLYqAEW2wwkzkXdCnsYltDyo8kbmjfw"],
        "author": 1,
        "replies": [],
        "root": 3,
        "quoted": None,
        "retweeted": None,
        "likedBy": [],
        "fakeTime": 2,
        "realTime": 2,
        "views": 0
    },
    {
        "id": 4,
        "text": "This is a tweet with a quoted tweet",
        "images": [],
        "author": 2,
        "replies": [],
        "root": 4,
        "quoted": 3,
        "retweeted": None,
        "likedBy": [],
        "fakeTime": 3,
        "realTime": 3,
        "views": 0
    },
    {
        "id": 5,
        "text": "This is a tweet with a retweet",
        "images": [],
        "author": 1,
        "replies": [],
        "root": 5,
        "quoted": None,
        "retweeted": 4,
        "likedBy": [],
        "fakeTime": 4
    }
]