import { useEffect, useState } from "react";
import { getTimeline } from "../services/database";
import { useLocation } from "react-router-dom";
import Tweet from "./Tweet";
import { useTheme } from "./ThemeContext";
import TweetCount from "./TweetCount";
import Loading from "./Loading";

function Feed() {
  const location = useLocation();
  const [tweets, setTweets] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const { theme } = useTheme();

  const queryParams = new URLSearchParams(location.search);
  const fakeTime = queryParams.get("fakeTime");
  const userId = queryParams.get("userId");

  useEffect(() => {
    async function fetchFeed() {
      setIsLoading(true);
      const newTweets = await getTimeline(userId, fakeTime);

      setTweets(newTweets);
      setIsLoading(false);
    }

    fetchFeed();
  }, [userId, fakeTime]);

  useEffect(() => {
    document.body.className = theme;
  }, [theme]);
  return (
    <div className="Feed">
      {isLoading && <Loading />}
      <div className="tweetList">
        {tweets
          ? tweets.map((tweet, index) => (
              <Tweet key={index} tweet={tweet} showStats={true} />
            ))
          : null}
      </div>
      {/* <TweetCount /> temporarily disabled */}
    </div>
  );
}

export default Feed;
