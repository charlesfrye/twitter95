"use client";

import { useEffect, useState, useContext } from "react";
import { useSearchParams } from 'next/navigation';
import Tweet from "./Tweet";
import User from "./User";
import { getProfile, getPosts } from "../services/database";
import Loading from "./Loading";
import { FakeTimeContext } from './FakeTimeContext';

function Profile({ userId }) {
  const [profile, setProfile] = useState({});
  const [isLoading, setIsLoading] = useState(false);

  const { fakeTime, setFakeTime } = useContext(FakeTimeContext);

  // any url param will set the fakeTime in the browsing session
  const queryParams = useSearchParams();
  if (queryParams.get("fakeTime")) {
    setFakeTime(queryParams.get("fakeTime"));
  }

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
    <div className="profile pt-4 flex flex-col justify-center items-center h-full space-y-8">
      {isLoading && <Loading />}
      {profile.user ? <User user={profile.user} bio={profile.bio} /> : null}

      {profile && profile.tweets && profile.tweets.length > 0 ? (
        profile.tweets.map((tweet, index) => (
          <div className="w-[600px]">
            <Tweet key={index} tweet={tweet} showStats={true} />
          </div>
        ))
      ) : (
        <p>No tweets found.</p>
      )}
    </div>
  );
}

export default Profile;
