import os

def post_to_real_twitter(tweet, author, image_bytes):
    import tweepy

    # Twitter API credentials
    api_key = os.getenv("TWITTER_API_KEY")
    api_secret = os.getenv("TWITTER_API_SECRET_KEY")
    access_token = os.getenv("TWITTER_ACCESS_TOKEN")
    access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

    # Media uses v1.1 api
    media_client = tweepy.API(tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_token_secret))
    
    # Posting uses v2 api
    post_client = tweepy.Client(consumer_key=api_key,
                           consumer_secret=api_secret, 
                           access_token=access_token, 
                           access_token_secret=access_token_secret)

    # Upload image as media
    image_filename = "/tmp/twitter-95-image.jpg"
    with open(image_filename, "wb") as f:
        f.write(image_bytes)
    media = media_client.media_upload(filename=image_filename)
    print("Media uploaded successfully:")
    print(media)
    os.remove(image_filename)

    # Post the tweet referencing the media
    
    words = tweet["text"].split(" ")
    hashtags = []
    for word in words:
        if word.startswith("#"):
            hashtags.append(word)
    hashtags = " ".join(hashtags)

    tweet_body = f"{author['display_name']} is going viral on twitter-95:\n\ntwitter-95.com/tweet/{tweet['tweet_id']}\n\n{hashtags}"

    resp = post_client.create_tweet(text=tweet_body, media_ids=[media.media_id])
    print("Tweet posted successfully:")
    print(f"Tweet URL: {resp}")
   