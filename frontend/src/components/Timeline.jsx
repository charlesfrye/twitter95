"use client";

import { useEffect, useState, useContext } from "react";
import { getTimeline } from "../services/database";
import { FakeTimeContext } from "./FakeTimeContext";
import { useSearchParams } from "next/navigation";
import Feed from "./Feed";

function Timeline() {
  const [tweets, setTweets] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const { fakeTime, setFakeTime } = useContext(FakeTimeContext);
  // any url param will set the fakeTime in the browsing session
  const queryParams = useSearchParams();
  if (queryParams.get("fakeTime")) {
    setFakeTime(queryParams.get("fakeTime"));
  }

  const userId = queryParams.get("userId");

  useEffect(() => {
    async function fetchFeed() {
      setIsLoading(true);
      const newTweets = await getTimeline(userId, fakeTime);

      setTweets(newTweets);
      setIsLoading(false);
    }

    fetchFeed();
  }, [userId, fakeTime]);

  return <Feed isLoading={isLoading} tweets={tweets} />;
}

export default Timeline;
