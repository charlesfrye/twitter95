from datetime import datetime, timedelta
import os
from typing import List, Optional

import fastapi
import modal
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import common


image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "asyncpg==0.29.0", "sqlalchemy[asyncio]==2.0.30"
)


app = modal.App(
    "db-client",
    image=image,
    secrets=[modal.Secret.from_name("pgsql-secret"), modal.Secret.from_name("api-key")],
)


@app.function(
    keep_warm=1,
    allow_concurrent_inputs=1000,
    concurrency_limit=1,
    mounts=[common.mount],
)
@modal.asgi_app()
def api() -> FastAPI:
    """API for accessing the Twitter '95 database.

    The primary routes for the bot client and the frontend are:
        - GET /timeline/, which returns fake-time-limited tweets based on user follows
        - GET /posts/, which returns fake-time-limited tweets from a specific user
        - GET /profile/, which returns the user and their bio
        - GET /trending/, which returns popular recent hashtags
        - GET /hashtag/, which returns fake-time-limited tweets based on hashtag
        - GET /tweet/{tweet_id}, which returns a specific tweet
        - POST /tweet/, which creates a new tweet

    The remaining routes are lower level (e.g. retrieving all tweets).
    """
    import sqlalchemy
    from sqlalchemy import and_, asc, delete, desc, insert, or_
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.future import select
    from sqlalchemy.orm import joinedload, sessionmaker
    from sqlalchemy.sql import text

    import common.models as models

    api = FastAPI(
        title="twitter95",
        summary="What if Twitter was made in 1995?",
        version="0.1.0",
        docs_url="/",
        redoc_url=None,
    )

    def connect():
        user = os.environ["PGUSER"]
        password = os.environ["PGPASSWORD"]
        host = os.environ["PGHOST"]
        port = os.environ["PGPORT"]
        database = os.environ["PGDATABASE"]

        connection_string = (
            f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}"
        )

        engine = create_async_engine(
            connection_string,
            isolation_level="READ COMMITTED",  # default and lowest level in pgSQL
            echo=True,  # log SQL as it is emitted
        )

        return engine

    engine = connect()

    new_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    api.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    token = os.environ["TWITTER95_API_KEY"]
    http_bearer = fastapi.security.HTTPBearer(
        scheme_name="Bearer Token",
        description="Authentication required for write/delete routes.",
    )

    # security: inject dependency on authed routes
    async def is_authenticated(api_key: str = fastapi.Security(http_bearer)):
        if api_key.credentials != token:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
        return {"username": "authenticated_user"}

    @api.get("/timeline/", response_model=List[models.pydantic.FullTweetRead])
    async def read_timeline(
        fake_time: Optional[datetime] = None,
        user_name: Optional[str] = None,
        limit: int = 10,
        ascending: bool = False,
    ):
        """Read the timeline at a specific (fake) time."""
        if fake_time is None:
            fake_time = common.to_fake(datetime.utcnow())
        sort = asc if ascending else desc
        async with new_session() as db:
            if user_name is not None:
                user_id_query = select(models.sql.User.user_id).where(
                    models.sql.User.user_name == user_name
                )
                user_result = await db.execute(user_id_query)
                user_id = user_result.scalar_one_or_none()

                if user_id is None:
                    raise fastapi.HTTPException(
                        status_code=404, detail=f"User {user_name} not found"
                    )

                followed_users = select(
                    models.sql.followers_association.c.followed_id
                ).where(models.sql.followers_association.c.follower_id == user_id)

            query = (
                select(models.sql.Tweet, models.sql.User)
                .join(
                    models.sql.User,
                    models.sql.Tweet.author_id == models.sql.User.user_id,
                )
                .filter(
                    or_(
                        models.sql.Tweet.fake_time <= fake_time,
                        models.sql.Tweet.fake_time == None,  # noqa: E711
                    )
                )
                .order_by(
                    sort(models.sql.Tweet.fake_time), sort(models.sql.Tweet.tweet_id)
                )
                .limit(limit)
                .options(
                    joinedload(models.sql.Tweet.author),
                    joinedload(models.sql.Tweet.quoted_tweet).joinedload(
                        models.sql.Tweet.author
                    ),
                )
            )
            if user_name is not None:
                query = query.where(models.sql.Tweet.author_id.in_(followed_users))
            else:
                query = query.where(
                    models.sql.Tweet.author_id != 3
                )  # drop NYT bot from timeline

            result = await db.execute(query)

            tweets = result.scalars().all()

        return list(tweets)
    
    @api.get("/tweet/{tweet_id}/", response_model=models.pydantic.FullTweetRead)
    async def read_tweet(tweet_id: int):
        """Read a specific tweet."""
        async with new_session() as db:
            tweet_query = select(models.sql.Tweet, models.sql.User) \
                .join(
                    models.sql.User,
                    models.sql.Tweet.author_id == models.sql.User.user_id,
                ) \
                .where(models.sql.Tweet.tweet_id == tweet_id) \
                .options(
                    joinedload(models.sql.Tweet.author),
                    joinedload(models.sql.Tweet.quoted_tweet).joinedload(
                        models.sql.Tweet.author
                    ),
                )
            
            result = await db.execute(tweet_query)
            tweet = result.scalar_one_or_none()
            
        if tweet is None:
            raise fastapi.HTTPException(
                status_code=404, detail=f"Tweet {tweet_id} not found"
            )
        
        return tweet

    @api.get("/posts/", response_model=List[models.pydantic.FullTweetRead])
    async def read_posts(
        user_name: str,
        fake_time: Optional[datetime] = None,
        limit: int = 10,
        ascending: bool = False,
    ):
        """Read a specific user's tweets at a specific (fake) time."""
        if fake_time is None:
            fake_time = common.to_fake(datetime.utcnow())
        sort = asc if ascending else desc
        async with new_session() as db:
            results = await db.execute(
                select(models.sql.Tweet)
                .join(
                    models.sql.User,
                    models.sql.Tweet.author_id == models.sql.User.user_id,
                )
                .filter(
                    and_(
                        or_(
                            models.sql.Tweet.fake_time <= fake_time,
                            models.sql.Tweet.fake_time == None,  # noqa: E711
                        ),
                    ),
                    models.sql.User.user_name == user_name,
                )
                .order_by(
                    sort(models.sql.Tweet.fake_time), sort(models.sql.Tweet.tweet_id)
                )
                .limit(limit)
                .options(
                    joinedload(models.sql.Tweet.author),
                    joinedload(models.sql.Tweet.quoted_tweet).joinedload(
                        models.sql.Tweet.author
                    ),
                )
            )
            posts = results.scalars().all()

        # we only load one layer of quoted tweets; null them out
        for post in posts:
            if post.quoted_tweet is not None:
                post.quoted_tweet.quoted_tweet = None

        return list(posts)

    @api.get(
        "/hashtag/{hashtag_text}", response_model=List[models.pydantic.FullTweetRead]
    )
    async def read_hashtag(
        hashtag_text: str,
        fake_time: Optional[datetime] = None,
        limit: int = 10,
        ascending: bool = False,
    ):
        """Read a specific hashtag's tweets at a specific (fake) time."""
        if fake_time is None:
            fake_time = common.to_fake(datetime.utcnow())
        hashtag_text = f"#{hashtag_text}"
        sort = asc if ascending else desc
        async with new_session() as db:
            results = await db.execute(
                select(models.sql.Tweet)
                .join(
                    models.sql.TweetHashtag,
                    models.sql.Tweet.tweet_id == models.sql.TweetHashtag.tweet_id,
                )
                .join(
                    models.sql.Hashtag,
                    models.sql.TweetHashtag.hashtag_id == models.sql.Hashtag.hashtag_id,
                )
                .filter(
                    and_(
                        or_(
                            models.sql.Tweet.fake_time <= fake_time,
                            models.sql.Tweet.fake_time == None,  # noqa: E711
                        ),
                    ),
                    models.sql.Hashtag.text == hashtag_text,
                )
                .order_by(
                    sort(models.sql.Tweet.fake_time), sort(models.sql.Tweet.tweet_id)
                )
                .limit(limit)
                .options(
                    joinedload(models.sql.Tweet.author),
                    joinedload(models.sql.Tweet.quoted_tweet).joinedload(
                        models.sql.Tweet.author
                    ),
                )
            )
            posts = results.scalars().all()

        # we only load one layer of quoted tweets; null them out
        for post in posts:
            if post.quoted_tweet is not None:
                post.quoted_tweet.quoted_tweet = None

        return list(posts)

    @api.get("/trending/", response_model=List[str])
    async def read_trending(
        fake_time: Optional[datetime] = None,
        limit: int = 10,
    ):
        """Return popular recent hashtags."""
        if fake_time is None:
            fake_time = common.to_fake(datetime.utcnow())

        start_time = fake_time - timedelta(hours=24)

        async with new_session() as db:
            results = await db.execute(
                select(
                    models.sql.Hashtag.text,
                    sqlalchemy.func.count(models.sql.TweetHashtag.hashtag_id).label(
                        "count"
                    ),
                )
                .join(
                    models.sql.TweetHashtag,
                    models.sql.Hashtag.hashtag_id == models.sql.TweetHashtag.hashtag_id,
                )
                .join(
                    models.sql.Tweet,
                    models.sql.TweetHashtag.tweet_id == models.sql.Tweet.tweet_id,
                )
                .filter(
                    and_(
                        models.sql.Tweet.fake_time <= fake_time,
                        models.sql.Tweet.fake_time >= start_time,
                    )
                )
                .group_by(models.sql.Hashtag.text)
                .order_by(desc("count"))
                .limit(limit)
            )

        hashtags = [row.text for row in results]

        return hashtags

    @api.get("/profile/{user_name}/", response_model=models.pydantic.ProfileRead)
    async def read_profile(user_name: str):
        """Read the profile information of a user."""
        async with new_session() as db:
            result = await db.execute(
                select(models.sql.User).filter_by(user_name=user_name)
            )
            user = result.scalar_one_or_none()
            if user is None:
                raise fastapi.HTTPException(status_code=404, detail="User not found")
            bio = await user.awaitable_attrs.bio

        if bio is None:
            return models.pydantic.ProfileRead(
                user=user,
                bio={"user_id": user.user_id},
            )

        return {"user": user, "bio": bio}

    @api.post(
        "/tweet/",
        response_model=models.pydantic.TweetRead,
        dependencies=[fastapi.Depends(is_authenticated)],
    )
    async def create_tweet(tweet: models.pydantic.TweetCreate):
        """Create a new tweet."""
        tweet = models.sql.Tweet(**tweet.dict())
        hashtags = common.utils.extract_hashtags(tweet.text)

        async with new_session() as db:
            try:
                # count quote tweets
                if tweet.quoted:
                    quoted_tweet = await db.get(models.sql.Tweet, tweet.quoted)
                    if quoted_tweet:
                        quoted_tweet.quotes += 1
                db.add(tweet)
                await db.flush()

                # handle hashtags
                for hashtag_text in hashtags:
                    hashtag = (
                        await db.execute(
                            select(models.sql.Hashtag).where(
                                models.sql.Hashtag.text == hashtag_text
                            )
                        )
                    ).scalar_one_or_none()

                    # if new hashtag, add to table
                    if not hashtag:
                        hashtag = models.sql.Hashtag(text=hashtag_text)
                        db.add(hashtag)
                        await db.flush()

                    # update tweet-hashtag mapping table
                    tweet_hashtag = models.sql.TweetHashtag(
                        tweet_id=tweet.tweet_id, hashtag_id=hashtag.hashtag_id
                    )
                    db.add(tweet_hashtag)

                await db.commit()
                await db.refresh(tweet)
            except sqlalchemy.exc.IntegrityError as e:
                raise fastapi.HTTPException(status_code=422, detail=f"Error: {e.orig}")

        return tweet

    @api.post("/edge/", dependencies=[fastapi.Depends(is_authenticated)])
    async def create_edge(_from: int, _to: int):
        """Add a directed "follows" edge to the social graph.

        Tweets flow in the direction of arrows."""
        async with new_session() as db:
            try:
                stmt = insert(models.sql.followers_association).values(
                    follower_id=_to, followed_id=_from
                )
                await db.execute(stmt)
                await db.commit()
            except sqlalchemy.exc.IntegrityError as e:
                raise fastapi.HTTPException(status_code=422, detail=f"Error: {e.orig}")

    @api.get("/tweets/", response_model=List[models.pydantic.TweetRead])
    async def read_tweets(limit=10, ascending: bool = False):
        """Read multiple tweets."""
        sort = asc if ascending else desc
        async with new_session() as db:
            result = await db.execute(
                select(models.sql.Tweet)
                .order_by(
                    sort(models.sql.Tweet.fake_time), sort(models.sql.Tweet.tweet_id)
                )
                .limit(limit)
            )
            tweets = result.scalars()
        return list(tweets)

    @api.post(
        "/users/",
        response_model=models.pydantic.UserRead,
        dependencies=[fastapi.Depends(is_authenticated)],
    )
    async def create_user(user: models.pydantic.UserCreate):
        """Create a new User."""
        if user.bio is not None:
            bio = models.sql.Bio(**user.bio.dict())
            del user.bio
        else:
            bio = None
        async with new_session() as db:
            try:
                user = models.sql.User(**user.dict())
                db.add(user)
                await db.commit()
                await db.refresh(user)
                if bio is not None:
                    bio.user_id = user.user_id
                    db.add(bio)
                    await db.commit()
            except sqlalchemy.exc.IntegrityError as e:
                raise fastapi.HTTPException(status_code=422, detail=f"Error: {e.orig}")

        # TODO: from_orm
        user = models.pydantic.UserRead(**user.__dict__)

        return user

    @api.get("/users/", response_model=List[models.pydantic.UserRead])
    async def read_users(ascending: bool = False, limit: int = 10):
        """Read multiple users."""
        async with new_session() as db:
            users = await db.scalars(
                select(models.sql.User)
                .order_by(
                    models.sql.User.user_id
                    if ascending
                    else desc(models.sql.User.user_id)
                )
                .limit(limit)
            )

        return list(users)

    @api.get("/users/{user_id}/")
    async def read_user(user_id: int) -> models.pydantic.UserRead:
        """Read a specific user"""
        async with new_session() as db:
            result = await db.execute(
                select(models.sql.User).filter_by(user_id=user_id)
            )
            user = result.scalar_one_or_none()
        if user is None:
            raise fastapi.HTTPException(
                status_code=404, detail=f"User {user_id} not found"
            )
        return user

    @api.delete("/users/{user_id}/", dependencies=[fastapi.Depends(is_authenticated)])
    async def delete_user(user_id: int):
        """Delete a user and all their data."""
        async with new_session() as db:
            result = await db.execute(
                select(models.sql.User).filter_by(user_id=user_id)
            )
            user = result.scalar_one_or_none()
            if user is None:
                raise fastapi.HTTPException(
                    status_code=404, detail=f"User {user_id} not found"
                )

            # remove tweets
            await db.execute(
                delete(models.sql.Tweet).where(models.sql.Tweet.author_id == user_id)
            )

            # remove following edges
            await db.execute(
                delete(models.sql.followers_association).where(
                    models.sql.followers_association.c.follower_id == user_id
                )
            )

            # remove followed edges
            await db.execute(
                delete(models.sql.followers_association).where(
                    models.sql.followers_association.c.followed_id == user_id
                )
            )

            # remove bio
            await db.execute(
                delete(models.sql.Bio).where(models.sql.Bio.user_id == user_id)
            )

            # remove the user
            await db.delete(user)

            await db.commit()

    @api.delete("/tweet/{tweet_id}", dependencies=[fastapi.Depends(is_authenticated)])
    async def delete_tweet(tweet_id: int):
        """Delete a tweet entirely.

        Fails if any other tweet is quoting this tweet."""
        async with new_session() as db:
            try:
                await db.execute(
                    delete(models.sql.Tweet).where(
                        models.sql.Tweet.tweet_id == tweet_id
                    )
                )
            except sqlalchemy.exc.IntegrityError as e:
                raise fastapi.HTTPException(status_code=422, detail=f"Error: {e.orig}")

            await db.commit()

    @api.get("/users/{user_id}/tweets/", response_model=List[models.pydantic.TweetRead])
    async def read_user_tweets(user_id: int, limit=10):
        """Read all tweets by a user."""
        async with new_session() as db:
            result = await db.execute(
                select(models.sql.User).filter_by(user_id=user_id)
            )
            user = result.scalar_one_or_none()
            if user is None:
                raise fastapi.HTTPException(
                    status_code=404, detail=f"User {user_id} not found"
                )

            result = await db.scalars(
                select(models.sql.Tweet)
                .filter_by(author_id=user_id)
                .order_by(
                    desc(models.sql.Tweet.fake_time), desc(models.sql.Tweet.tweet_id)
                )
                .limit(limit)
            )
            tweets = result.all()

        return list(tweets)

    @api.get("/names/{user_name}/")
    async def read_user_by_name(user_name: str) -> models.pydantic.UserRead:
        """Read a specific user by their user_name."""
        async with new_session() as db:
            result = await db.execute(
                select(models.sql.User).filter_by(user_name=user_name)
            )
            user = result.scalar_one_or_none()
            if user is None:
                raise fastapi.HTTPException(
                    status_code=404, detail=f"User {user_name} not found"
                )
        return user

    @api.post("/query/", dependencies=[fastapi.Depends(is_authenticated)])
    async def execute_query(request: dict):
        """Execute a raw SQL query."""
        query = request.get("query")
        if not query:
            raise fastapi.HTTPException(
                status_code=400, detail="No SQL query provided."
            )

        async with new_session() as db:
            result = await db.execute(text(query))
            # no commit, so auto-rollback of anything destructive and this is "safe"
            return {"result": [dict(row) for row in result.mappings()]}

    return api
