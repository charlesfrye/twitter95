import { useEffect, useState } from "react";
import { useParams, useLocation } from "react-router-dom";
import { getHashtag } from "../services/database";
import Tweet from "./Tweet";
import TweetCount from "./TweetCount";
import Loading from "./Loading";

function HashtagFeed() {
  const location = useLocation();
  const { hashtagText } = useParams();
  const [tweets, setTweets] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const queryParams = new URLSearchParams(location.search);
  const fakeTime = queryParams.get("fakeTime");
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
              <Tweet key={index} tweet={tweet} showStats={true} />
            ))
          : null}
      </div>
      {/* <TweetCount /> temporarily disabled */}
    </div>
  );
}

export default HashtagFeed;
