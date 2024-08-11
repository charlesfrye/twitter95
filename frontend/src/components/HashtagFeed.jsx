import { useEffect, useState, useContext } from "react";
import { useParams, useLocation } from "react-router-dom";
import { getHashtag } from "../services/database";
import Tweet from "./Tweet";
import { FakeTimeContext } from './FakeTimeContext';
import Loading from "./Loading";

function HashtagFeed() {
  const location = useLocation();
  const { hashtagText } = useParams();
  const [tweets, setTweets] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const { fakeTime, setFakeTime } = useContext(FakeTimeContext);
  // any url param will set the fakeTime in the browsing session
  const queryParams = new URLSearchParams(location.search);
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
              <Tweet key={index} tweet={tweet} showStats={true} />
            ))
          : null}
      </div>
      {/* <TweetCount /> temporarily disabled */}
    </div>
  );
}

export default HashtagFeed;
