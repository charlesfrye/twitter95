"use client";
import PropTypes from "prop-types";
import styled from "styled-components";
import { useRouter, useSearchParams } from "next/navigation";
import {
  MenuList,
  MenuListItem as React95MenuListItem,
  Separator,
  Button,
  Counter,
} from "react95";
import TweetContent from "./TweetContent";
import { useContext } from "react";
import { FakeTimeContext } from "./FakeTimeContext";

const MenuListItem = styled(React95MenuListItem)`
  &:hover {
    color: inherit;
    background: none;
  }
`;

function formatFakeTime(fakeTimeStr) {
  const date = new Date(fakeTimeStr);
  const formattedDateTime = new Intl.DateTimeFormat("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    hour12: true,
  }).format(date);

  return formattedDateTime;
}

function Tweet({ tweet, showStats, showQuoted = true }) {
  const router = useRouter();

  const author = tweet.author;

  const { setFakeTime } = useContext(FakeTimeContext);
  // any url param will set the fakeTime in the browsing session
  const queryParams = useSearchParams();
  if (queryParams.get("fakeTime")) {
    setFakeTime(queryParams.get("fakeTime"));
  }

  const handleTweetClick = () => {
    router.push(`/tweet/${tweet.tweet_id}`);
  };

  const handleProfileClick = () => {
    router.push(`/profile/${author.user_name}`);
  };

  const handleRetweetClick = () => {
    const url = `https://twitter-95.com/tweet/${tweet.tweet_id}`;
    const text = `Check out this tweet from 1995 by ${author.user_name}:%0A%0A${url}`;
    const tweetContent = `https://x.com/intent/post?text=${text}`;
    window.open(tweetContent, "_blank");
  };

  return (
    tweet && (
      <div>
        <MenuList className="flex flex-col !py-2">
          <MenuListItem
            className="cursor-pointer text-sm overflow-hidden whitespace-nowrap"
            onClick={handleProfileClick}
          >
            {author.profile_pic && (
              <img
                src={author.profile_pic}
                alt={author.user_name}
                style={{
                  width: 40,
                  height: 40,
                  border: "2px solid",
                  borderTopColor: "rgb(132, 133, 132)",
                  borderRightColor: "rgb(254, 254, 254)",
                  borderBottomColor: "rgb(254, 254, 254)",
                  borderLeftColor: "rgb(132, 133, 132)",
                }}
              />
            )}
            {`@${author.user_name} on ${formatFakeTime(tweet.fake_time)}`}
          </MenuListItem>
          <Separator className="!my-2" />
          <MenuListItem
            size="sm"
            className="whitespace-normal text-left min-h-24 flex-1 cursor-pointer"
            onClick={handleTweetClick}
          >
            <TweetContent tweet={tweet} />
          </MenuListItem>
          {tweet.quoted && tweet.quoted_tweet && showQuoted && (
            <div className="p-2">
              <Tweet tweet={tweet.quoted_tweet} showStats={false} />
            </div>
          )}

          <div className="flex items-center justify-center">
            <div className="flex space-x-10 h-fit">
              {showStats && (
                <div className="flex items-center justify-center space-x-5">
                  <p className="text-xl">QTs:</p>
                  <Counter value={tweet.quotes} minLength={3} />
                </div>
              )}
              <div className="flex items-center justify-center space-x-5 py-2">
                <Button onClick={handleRetweetClick}>Retweet</Button>
              </div>
            </div>
          </div>
        </MenuList>
      </div>
    )
  );
}

Tweet.propTypes = {
  tweet: PropTypes.shape({
    author: PropTypes.shape({
      user_id: PropTypes.number,
      user_name: PropTypes.string,
      display_name: PropTypes.string,
      profile_pic: PropTypes.string,
    }),
    tweet_id: PropTypes.number,
    text: PropTypes.string,
    likes: PropTypes.number,
    quotes: PropTypes.number,
    fake_time: PropTypes.string,
    author_id: PropTypes.number,
    quoted: PropTypes.number,
    quoted_tweet: PropTypes.object, // recursive, depth 1
  }),
};

export default Tweet;
