"use client";

import Tweet from "./Tweet";
import Loading from "./Loading";

function Feed({ isLoading, tweets }) {
  return (
    <div className="Feed">
      {isLoading && <Loading />}
      <div className="tweetList">
        {tweets
          ? tweets.map((tweet, index) => (
              <Tweet key={index} tweet={tweet} showStats={true} />
            ))
          : null}
      </div>
    </div>
  );
}

export default Feed;
