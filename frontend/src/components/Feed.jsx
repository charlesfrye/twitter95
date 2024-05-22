import { useEffect, useState } from "react";
import { getTimeline } from "../services/database";
import Tweet from "./Tweet";
import { useTheme } from "./ThemeContext";
import TweetCount from "./TweetCount";
import Loading from "./Loading";

function Feed() {
  const [tweets, setTweets] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const { theme } = useTheme();


  useEffect(() => {
    async function fetchFeed() {
      setIsLoading(true);
      const newTweets = await getTimeline();

      setTweets(newTweets);
      setIsLoading(false);
    }

    fetchFeed();
  }, []);

  useEffect(() => {
    document.body.className = theme;
  }, [theme]);
  return (
    <div className="Feed">
      {isLoading && <Loading />}
      <div className="tweetList">
        {tweets
          ? tweets.map((tweet, index) => <Tweet key={index} tweet={tweet} />)
          : null}
      </div>
      <TweetCount />
    </div>
  );
}

export default Feed;
