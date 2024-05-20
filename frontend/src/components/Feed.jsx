import { useEffect, useState } from "react";
import { getTimeline } from "../services/database";
import Tweet from "./Tweet";
import { useTheme } from "./ThemeContext";

function Feed() {
  const [tweets, setTweets] = useState([]);
  const { theme } = useTheme();

  useEffect(() => {
    async function fetchFeed() {
      const newTweets = await getTimeline();

      setTweets(newTweets);
    }

    fetchFeed();
  }, []);

  useEffect(() => {
    document.body.className = theme;
  }, [theme]);
  return (
    <div className="Feed">
      <div className="tweetList">
        {tweets
          ? tweets.map((tweet, index) => (
              <Tweet key={index} authorTweet={tweet} />
            ))
          : null}
      </div>
    </div>
  );
}

export default Feed;
