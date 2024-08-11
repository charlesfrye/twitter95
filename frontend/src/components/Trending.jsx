import { useEffect, useState, useContext } from "react";
import { getTrending } from "../services/database";
import { useLocation } from "react-router-dom";
import TrendingHashtag from "./TrendingHashtag";
import Loading from "./Loading";
import { FakeTimeContext } from './FakeTimeContext';

function Trending() {
  const location = useLocation();
  const [trending, setTrending] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const { fakeTime, setFakeTime } = useContext(FakeTimeContext);
  // any url param will set the fakeTime in the browsing session
  const queryParams = new URLSearchParams(location.search);
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
