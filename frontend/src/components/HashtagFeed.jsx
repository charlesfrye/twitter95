"use client";

import { useEffect, useState, useContext } from "react";
import { useSearchParams } from 'next/navigation';
import { getHashtag } from "../services/database";
import Tweet from "./Tweet";
import { FakeTimeContext } from './FakeTimeContext';
import Loading from "./Loading";

function HashtagFeed({ hashtagText }) {

  const [tweets, setTweets] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const { fakeTime, setFakeTime } = useContext(FakeTimeContext);
  // any url param will set the fakeTime in the browsing session
  const queryParams = useSearchParams();
  if (queryParams.get("fakeTime")) {
    setFakeTime(queryParams.get("fakeTime"));
  }

  const limit = queryParams.get("limit");

  useEffect(() => {
    async function fetchHashtagFeed() {
      setIsLoading(true);
      const newTweets = await getHashtag(hashtagText, fakeTime, limit);

      setTweets(newTweets);
      setIsLoading(false);
    }

    fetchHashtagFeed();
  }, [hashtagText, fakeTime, limit]);

  return (
    <div className="HashtagFeed">
      {isLoading && <Loading />}
      <div className="tweetList">
        {tweets
          ? tweets.map((tweet, index) => (
            <div className="w-[600px]">
              <Tweet key={index} tweet={tweet} showStats={true} />
            </div>
            ))
          : null}
      </div>
    </div>
  );
}

export default HashtagFeed;
