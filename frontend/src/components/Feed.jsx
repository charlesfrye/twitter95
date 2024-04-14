import { useEffect, useState } from "react";
import { getFeed } from "../services/database";
import Tweet from "./Tweet";
import ThemeSwitcher from "./ThemeSwitcher";
import { useTheme } from "./ThemeContext";

function Feed() {
  const [tweets, setTweets] = useState([]);
  const { theme } = useTheme();

  useEffect(() => {
    async function fetchFeed() {
      const newTweets = await getFeed();
      console.log(newTweets);
      setTweets(newTweets);
    }

    fetchFeed();
  }, []);

  useEffect(() => {
    document.body.className = theme;
    console.log("Theme updated in Feed:", theme);
  }, [theme]);
  return (
    <div className="Feed">
      <div className="tweetList">
        <p>hello</p>
        {tweets
          ? tweets.map((tweet, index) => <Tweet key={index} tweet={tweet} />)
          : null}
      </div>
      <div className="Settings">
        <ThemeSwitcher />
      </div>
    </div>
  );
}

export default Feed;
