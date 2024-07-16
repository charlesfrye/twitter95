import { useEffect, useState } from "react";
import { useParams, useLocation } from "react-router-dom";
import Tweet from "./Tweet";
import User from "./User";
import { getProfile, getPosts } from "../services/database";
import Loading from "./Loading";

function Profile() {
  const location = useLocation();
  const { userId } = useParams();
  const [profile, setProfile] = useState({});
  const [isLoading, setIsLoading] = useState(false);

  const queryParams = new URLSearchParams(location.search);
  const fakeTime = queryParams.get("fakeTime");

  useEffect(() => {
    async function fetchData() {
      setIsLoading(true);
      try {
        const [userData, userTweets] = await Promise.all([
          getProfile(userId),
          getPosts(userId, fakeTime, 20),
        ]);

        setProfile({ ...userData, tweets: userTweets });
      } catch (error) {
        console.error("Error fetching data:", error);
      }
      setIsLoading(false);
    }

    fetchData();
  }, [userId, fakeTime]);

  return (
    <div className="profile pt-4">
      {isLoading && <Loading />}
      {profile.user ? <User user={profile.user} bio={profile.bio} /> : null}

      {profile && profile.tweets && profile.tweets.length > 0 ? (
        profile.tweets.map((tweet, index) => (
          <Tweet key={index} tweet={tweet} showStats={true} />
        ))
      ) : (
        <p>No tweets found.</p>
      )}
    </div>
  );
}

export default Profile;
