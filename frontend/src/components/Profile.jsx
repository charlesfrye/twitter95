import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import Tweet from "./Tweet";
import User from "./User";
import { getProfile, getPosts } from "../services/database";

function Profile() {
  const { userId } = useParams();
  const [profile, setProfile] = useState({});

  useEffect(() => {
    async function fetchData() {
      try {
        const [userData, userTweets] = await Promise.all([
          getProfile(userId),
          getPosts(userId),
        ]);

        setProfile({ ...userData, tweets: userTweets });
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    }

    fetchData();
  }, [userId]);

  return (
    <div className="profile">
      {profile.user ? <User user={profile.user} bio={profile.bio} /> : null}

      {profile && profile.tweets && profile.tweets.length > 0 ? (
        profile.tweets.map((tweet, index) => (
          <Tweet
            key={index}
            authorTweet={{ author: profile.user, tweet: tweet }}
          />
        ))
      ) : (
        <p>No tweets found.</p>
      )}
    </div>
  );
}

export default Profile;
