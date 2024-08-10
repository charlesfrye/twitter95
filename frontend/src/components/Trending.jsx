import { useEffect, useState } from "react";
import { getTrending } from "../services/database";
import { useLocation } from "react-router-dom";
import TrendingHashtag from "./TrendingHashtag";
import Loading from "./Loading";

function Trending() {
  const location = useLocation();
  const [trending, setTrending] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const queryParams = new URLSearchParams(location.search);
  const fakeTime = queryParams.get("fakeTime");

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
