"use client";

import { useParams } from "react-router-dom";
import Tweet from "./Tweet";
import { getTweet } from "../services/database";
import { useEffect, useState } from "react";
import { useRouter } from 'next/navigation';

function TweetPage() {
  const router = useRouter();
  // pull tweetID from url /tweet/:tweetId?render_as_og=true
  const tweetId = useParams().tweetId;

  const queryParams = new URLSearchParams(location.search);
  const render_as_og = queryParams.get("render_as_og");

  // fetch tweet from backend
  const [tweet, setTweet] = useState(undefined);

  useEffect(() => {
    async function fetchTweet() {
      if (tweetId) {
        const fetched_tweet = await getTweet(tweetId);
        setTweet(fetched_tweet);
      } else {
        // redirect to home page
        router.push("/timeline");
      }
    }
    fetchTweet();
  }, [tweetId]);

  if (render_as_og) {
    return (
      <div className="absolute top-0 left-0 w-[800px] h-[450px]">
        <div className="flex justify-center items-center h-full">
          <div className="h-fit scale-125">
            {tweet ? (
              <Tweet tweet={tweet} showStats={true} showQuoted={false} />
            ) : (
              <p>Loading...</p>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="banner align-middle mt-4">
      {tweet ? <Tweet tweet={tweet} showStats={true} /> : <p>Loading...</p>}
    </div>
  );
}
export default TweetPage;
