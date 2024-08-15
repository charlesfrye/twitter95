"use client";

import Tweet from "./Tweet";
import Loading from "./Loading";

function Feed({ isLoading, tweets }) {
  return (
    <div className="mt-4">
      {isLoading && <Loading />}
      <div className="flex flex-col justify-center items-center h-full space-y-8">
        {tweets
          ? tweets.map((tweet, index) => (
              <div className="w-[600px]" key={index} >
                <Tweet tweet={tweet} showStats={true} />
              </div>
            ))
          : null}
      </div>
    </div>
  );
}

export default Feed;
