import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import Tweet from "./Tweet";
import Bio from "./Bio";
import User from "./User";
import { getUser, getUserTweets } from "../services/database";

function Profile() {
  const { userId } = useParams();
  const [tweets, setTweets] = useState([]);
  const [user, setUser] = useState({});
  const [bio, setBio] = useState({});

  useEffect(() => {
    async function fetchData() {
      try {
        const userData = await getUser(userId);
        const userTweets = await getUserTweets(userId);

        setUser(userData);
        setBio({ content: userData.bio, location: userData.location });
        setTweets(userTweets);
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    }

    fetchData();
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
