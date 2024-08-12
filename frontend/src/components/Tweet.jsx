import "./Tweet.css";
import PropTypes from "prop-types";
import styled from "styled-components";
import { useLocation, useNavigate } from "react-router-dom";
import {
  MenuList,
  MenuListItem as React95MenuListItem,
  Separator,
  Button,
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
  const navigate = useNavigate();
  const location = useLocation();
  const author = tweet.author;

  const { fakeTime, setFakeTime } = useContext(FakeTimeContext);
  // any url param will set the fakeTime in the browsing session
  const queryParams = new URLSearchParams(location.search);
  if (queryParams.get("fakeTime")) {
    setFakeTime(queryParams.get("fakeTime"));
  }

  const handleProfileClick = () => {
    const date = new Date(`${tweet.fake_time}Z`);
    date.setUTCSeconds(date.getUTCSeconds() + 1);
    const newFakeTime = date.toISOString().replace("Z", "");
    navigate(`/profile/${author.user_name}?fakeTime=${newFakeTime}`);
  };

  const handleRetweetClick = () => {
    const url = `https://twitter-95.com/tweet/${tweet.tweet_id}`;
    const text = `Check out this tweet from 1995 by ${author.user_name}:%0A%0A${url}`;
    const tweetContent = `https://x.com/intent/post?text=${text}`;
    window.open(tweetContent, "_blank");
  };

  return (
    tweet && (
      <div className="tweet">
        <MenuList className="!flex !flex-col text-ellipsis">
          <MenuListItem
            className="!cursor-pointer !text-sm !overflow-hidden !whitespace-nowrap !text-ellipsis"
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
          <Separator />
          <MenuListItem
            size="sm"
            className="!whitespace-normal !text-left !min-h-24 !flex-1"
          >
            <TweetContent tweet={tweet} />
          </MenuListItem>
          {tweet.quoted && tweet.quoted_tweet && showQuoted && (
            <Tweet tweet={tweet.quoted_tweet} showStats={false} />
          )}

          <div className="flex items-center justify-center">
            <div className="flex space-x-10">
              {showStats && <p className="py-[5px]">QTs: {tweet.quotes}</p>}
              <Button onClick={handleRetweetClick}>Retweet</Button>
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
