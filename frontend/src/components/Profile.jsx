import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import Tweet from "./Tweet";
import { getFeed } from "../services/database";

function Profile() {
  const { userId } = useParams();
  const [tweets, setTweets] = useState([]);

  useEffect(() => {
    async function fetchFeed() {
      const feed = await getFeed();
      const userTweets = feed.filter((tweet) => tweet.userId === userId);
      setTweets(userTweets);
    }
    fetchFeed();
  }, [userId]);

  return (
    <div className="profile">
      {tweets
        ? tweets.map((tweet, index) => <Tweet key={index} tweet={tweet} />)
        : console.log("No tweets found.")}
    </div>
  );
}

export default Profile;
