import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import Tweet from "./Tweet";
import Bio from "./Bio";
import User from "./User";
import { getFeed, getUser } from "../services/database";

function Profile() {
  const { userId } = useParams();
  const [tweets, setTweets] = useState([]);
  const [user, setUser] = useState({});
  const [bio, setBio] = useState({});

  useEffect(() => {
    async function fetchFeed() {
      const userData = await getUser(userId);
      setUser(userData);
      setBio({ content: userData.bio, location: userData.location }); // Adjusted to hypothetical user data structure
      const feed = await getFeed();
      const userTweets = feed.filter((tweet) => tweet.user_id === userId);
      setTweets(userTweets);
    }
    fetchFeed();
  }, [userId]);

  return (
    <div className="profile">
      <User user={user} />
      <Bio bio={bio} />
      {tweets.length > 0 ? (
        tweets.map((tweet, index) => <Tweet key={index} tweet={tweet} />)
      ) : (
        <p>No tweets found.</p>
      )}
    </div>
  );
}

export default Profile;
