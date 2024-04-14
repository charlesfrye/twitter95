import modal
import os
import pandas as pd
from datetime import datetime, timezone
from pydantic import BaseModel
from typing import Optional
import math

stub = modal.Stub("nyt_bot", secrets=[modal.Secret.from_name("nyt-api-key")])

class CreateTweetRequest(BaseModel):
    author: str
    text: str
    images: Optional[list[str]] = []
    faketime: Optional[datetime] = None
    
class CreateUserRequest(BaseModel):
    profilePic: str
    bannerPic: str
    username: str
    displayName: str
    
def generate_faketime_utc_timestamp(date, hour) -> datetime:
    """returns the datetime object for the given date and hour in UTC"""
    naive_datetime = datetime.strptime(f"{date} {hour}:00:00", "%Y-%m-%d %H:%M:%S")
    # Attach UTC timezone information
    utc_datetime = naive_datetime.replace(tzinfo=timezone.utc)
    return utc_datetime

def calculate_publish_hour(article_index, total_articles, start_index=0):
    if total_articles == 0:
        raise ValueError("Total articles must be greater than 0")
    
    normalized_index = article_index - start_index
    # 24 hours in a day
    hours_in_day = 24

    # Calculate the number of articles per hour
    articles_per_hour = total_articles / hours_in_day

    # Calculate which hour to publish the article in
    publish_hour = int(normalized_index / articles_per_hour)

    # Ensure that the hour doesn't exceed 23 due to integer division peculiarities
    publish_hour = min(publish_hour, hours_in_day - 1)
    
    return publish_hour

@stub.local_entrypoint()
def main():
    # Create NYT account
    create_req = CreateUserRequest(
        profilePic="https://1000logos.net/wp-content/uploads/2017/04/New-York-Times-emblem.jpg",
        bannerPic="https://1000logos.net/wp-content/uploads/2017/04/Font-New-York-Times-Logo.jpg",
        username="NewYorkTimes",
        displayName="New York Times Newspaper"
    )
    # call the create endpoint TBD
    
    # load CSV file from ../archive/new_york_times_stories_1995_april.csv of headlines and links
    file = "../archive/new_york_times_stories_1995_april.csv"
    df = pd.read_csv(file)
    print(df.head())
    # we only want headline, word_count, url, and pub_date
    df = df[["headline", "word_count", "url", "pub_date"]]
    print(df.head())
    
    for i in range(1, 30):
        start_index = 0
        # make sure i has 2 digits
        if i < 10:
            i = f"0{i}"
        articles_for_date = df[df["pub_date"] == f"1995-04-{i}T05:00:00+0000"]
        print(len(articles_for_date))
        # iterate through articles with index:
        for index, article in articles_for_date.iterrows():
            if start_index == 0:
                start_index = index
            tweet_req = CreateTweetRequest(
                author="nyt_bot", # todo: find ID
                text=article["headline"],
                faketime=generate_faketime_utc_timestamp(f"1995-04-{i}", calculate_publish_hour(index, len(articles_for_date), start_index)),
                images=[article["url"]]
            )
            print(tweet_req)
            
    # get the set of csv files for the day
    # divide by 24 hours
    # tweet out the headlines for the hour
    print("Hello, World!")