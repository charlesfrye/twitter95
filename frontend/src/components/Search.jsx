"use client";

import { useState, useEffect, useContext } from "react";
import Feed from "./Feed";
import TimeTravel from "./TimeTravel";
import SearchBar from "./SearchBar";
import { FakeTimeContext } from "./FakeTimeContext";
import { searchTweets } from "@/services/database";

function Search() {
  const [tweets, setTweets] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const { fakeTime, setFakeTime } = useContext(FakeTimeContext);
  // any url param will set the fakeTime in the browsing session
  const queryParams = new URLSearchParams(location.search);
  if (queryParams.get("fakeTime")) {
    setFakeTime(queryParams.get("fakeTime"));
  }

  const clearTweets = () => {
    setTweets([]);
  };

  const handleKeyDown = (event) => {
    if ((event.metaKey || event.ctrlKey) && event.key === "k") {
      event.preventDefault();
      clearTweets();
    }
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  };
  window.addEventListener("keydown", handleKeyDown);

  async function runSearch(searchQuery) {
    setIsLoading(true);
    const newTweets = await searchTweets(searchQuery, fakeTime);

    setTweets(newTweets);
    setIsLoading(false);
  }

  if (isLoading || tweets.length > 0) {
    return (
      <div>
        <h2
          className="text-center text-white mt-1 text-l cursor-pointer select-none"
          onClick={clearTweets}
        >
          Click here or press Cmd+K to search again
        </h2>
        <Feed isLoading={isLoading} tweets={tweets} />;
      </div>
    );
  } else {
    return (
      <div className="banner align-middle mt-4">
        <div className="flex flex-col">
          <TimeTravel />
          <SearchBar onButtonClick={runSearch} />
        </div>
      </div>
    );
  }
}

export default Search;
