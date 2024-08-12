"use client";

import { useEffect, useState, useContext } from "react";
import { getTrending } from "../services/database";
import { useSearchParams } from 'next/navigation';
import TrendingHashtag from "./TrendingHashtag";
import Loading from "./Loading";
import { FakeTimeContext } from './FakeTimeContext';

function Trending() {
  const [trending, setTrending] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const { fakeTime, setFakeTime } = useContext(FakeTimeContext);
  // any url param will set the fakeTime in the browsing session
  const queryParams = useSearchParams();
  if (queryParams.get("fakeTime")) {
    setFakeTime(queryParams.get("fakeTime"));
  }

  useEffect(() => {
    async function fetchTrending() {
      setIsLoading(true);
      const trending = await getTrending(fakeTime);

      setTrending(trending);
      setIsLoading(false);
    }

    fetchTrending();
  }, [fakeTime]);

  return (
    <div className="Trending">
      {isLoading && <Loading />}
      <div className="trendingList">
        {trending.length
          ? trending.map((hashtag, index) => (
              <TrendingHashtag key={index} text={hashtag} />
            ))
          : null}
      </div>
    </div>
  );
}

export default Trending;
