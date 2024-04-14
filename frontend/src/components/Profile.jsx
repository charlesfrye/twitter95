import { useEffect, useState } from "react";

import Tweet from "./Tweet";
import { getFeed } from "../services/database";

function Profile() {
  const [tweets, setTweets] = useState([]);

  useEffect(() => {
    async function fetchFeed() {
      const feed = await getFeed();
      setTweets(feed);
    }
    fetchFeed();
  }, []);

  return (
    <div className="profile">
      {tweets
        ? tweets.map((tweet, index) => <Tweet key={index} tweet={tweet} />)
        : null}
    </div>
  );
}

export default Profile;
