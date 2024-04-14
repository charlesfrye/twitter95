import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import Tweet from "./Tweet";
import { getFeed, getUser } from "../services/database";

function Profile() {
  const { userId } = useParams();
  const [tweets, setTweets] = useState([]);
  const [user, setUser] = useState({});
  const [bio, setBio] = useState({});

  useEffect(() => {
    async function fetchFeed() {
      const feed = await getFeed();
      const userTweets = feed.filter((tweet) => tweet.user_id === userId);
      const user = await getUser(userId);
      setUser(user);
      setBio(user.bio);
      setTweets(userTweets);
    }
    fetchFeed();
  }, [userId]);

  return (
    <div className="profile">
      <div className="header">
        <div className="userIinfo">
          <p1>{user.display_name}</p1>
          <p>{user.user_name}</p>
          <p>{user.profile_pic}</p>
          <p>{bio.content}</p>
          <p>{bio.location}</p>
        </div>
        {user.banner_pic}
      </div>
      {tweets
        ? tweets.map((tweet, index) => <Tweet key={index} tweet={tweet} />)
        : console.log("No tweets found.")}
    </div>
  );
}

export default Profile;
