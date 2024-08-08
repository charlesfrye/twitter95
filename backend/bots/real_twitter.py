import modal

image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "requests==2.32.3", "requests_oauthlib==2.0.0"
)

app = modal.App("real-twitter-bot", image=image)


@app.function(secrets=[modal.Secret.from_name("twitter-api")])
def go(payload: str = None, dryrun: bool = True):
    import os

    import requests
    from requests_oauthlib import OAuth1

    API_KEY = os.environ["TWITTER_API_KEY"]
    API_SECRET_KEY = os.environ["TWITTER_API_SECRET_KEY"]
    ACCESS_TOKEN = os.environ["TWITTER_ACCESS_TOKEN"]
    ACCESS_TOKEN_SECRET = os.environ["TWITTER_ACCESS_TOKEN_SECRET"]

    auth = OAuth1(API_KEY, API_SECRET_KEY, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    if not dryrun:
        url = "https://api.twitter.com/2/tweets"
        data = {"text": payload or "This is a test tweet from my bot on Modal."}
        response = requests.post(url, auth=auth, json=data)
    else:
        url = "https://api.twitter.com/1.1/account/verify_credentials.json"
        response = requests.get(url, auth=auth)

    if response.status_code < 400:
        print("API hit successfully.")
    else:
        print(f"Failed to hit API. Status code: {response.status_code}")
        response.raise_for_status()
    print(f"Response: {response.text}")
