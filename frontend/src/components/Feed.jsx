import { useEffect, useState } from "react";
import { getFeed } from "../services/database";
import Tweet from "./Tweet";

function Feed() {
  const [tweets, setTweets] = useState([]);

  useEffect(() => {
    async function fetchFeed() {
      const newTweets = await getFeed();
      console.log(newTweets);
      setTweets(newTweets);
    }

    fetchFeed();
  }, []);

  return (
    <div className="feed">
      <p>hello</p>
      {tweets
        ? tweets.map((tweet, index) => <Tweet key={index} tweet={tweet} />)
        : null}
    </div>
  );
}

export default Feed;
