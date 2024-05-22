import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import Tweet from "./Tweet";
import User from "./User";
import { getProfile, getPosts } from "../services/database";
import Loading from "./Loading";

function Profile() {
  const { userId } = useParams();
  const [profile, setProfile] = useState({});
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {

    async function fetchData() {
      setIsLoading(true);
      try {
        const [userData, userTweets] = await Promise.all([
          getProfile(userId),
          getPosts(userId),
        ]);

        setProfile({ ...userData, tweets: userTweets });
      } catch (error) {
        console.error("Error fetching data:", error);
      }
      setIsLoading(false);
    }

    fetchData();
  }, [userId]);

  return (

    <div className="profile">
      {isLoading && <Loading />}
      {profile.user ? <User user={profile.user} bio={profile.bio} /> : null}

      {profile && profile.tweets && profile.tweets.length > 0 ? (
        profile.tweets.map((tweet, index) => (
          <Tweet key={index} tweet={tweet} />
        ))
      ) : (
        <p>No tweets found.</p>
      )}
    </div>
  );
}

export default Profile;
