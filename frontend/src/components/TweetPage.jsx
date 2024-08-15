"use client";
import { useSearchParams, useRouter } from "next/navigation";
import Tweet from "./Tweet";
import { getTweet } from "../services/database";
import { useEffect, useState } from "react";

function TweetPage({ tweetID }) {
  const router = useRouter();
  // pull tweetID from url /tweet/:tweetID?render_as_og=true

  const queryParams = useSearchParams();
  const render_as_og = queryParams.get("render_as_og");

  // fetch tweet from backend
  const [tweet, setTweet] = useState(undefined);

  useEffect(() => {
    async function fetchTweet() {
      if (tweetID) {
        const fetched_tweet = await getTweet(tweetID);
        setTweet(fetched_tweet);
      } else {
        // redirect to home page
        router.push("/timeline");
      }
    }
    fetchTweet();
  }, [tweetID, router]);

  if (render_as_og) {
    return (
      <div className="absolute top-0 left-0 w-[800px] h-[450px]">
        <div className="flex justify-center items-center h-full">
          <div className="h-fit scale-125">
            {tweet ? (
              <div className="w-[600px]">
                <Tweet tweet={tweet} showStats={true} showQuoted={false} />
              </div>
            ) : (
              <p>Loading...</p>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col justify-center items-center h-full">
      {tweet ? 
        <div className="w-[600px]">
          <Tweet tweet={tweet} showStats={true} />
        </div>
        : <p>Loading...</p>}
    </div>
  );
}
export default TweetPage;
