import { useEffect, useState, useContext } from "react";
import { getTimeline } from "../services/database";
import { FakeTimeContext } from './FakeTimeContext';
import { useLocation } from "react-router-dom";
import Tweet from "./Tweet";
import Loading from "./Loading";

function Feed() {
  const location = useLocation();
  const [tweets, setTweets] = useState([]);
  const [isLoading, setIsLoading] = useState(false);


  const { fakeTime, setFakeTime } = useContext(FakeTimeContext);
  // any url param will set the fakeTime in the browsing session
  const queryParams = new URLSearchParams(location.search);
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
      {/* <TweetCount /> temporarily disabled */}
    </div>
  );
}

export default Feed;
