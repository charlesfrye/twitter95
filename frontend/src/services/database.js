const urlPrefix = "ex-twitter--db-client-api";

const urlSuffix =
  process.env.NEXT_PUBLIC_DEV_BACKEND === "true"
    ? "-dev.modal.run"
    : ".modal.run";

export const baseUrl = `https://${urlPrefix}${urlSuffix}`;

const deltaMilliseconds = 915235088 * 1000; // time from 1995 to 2024

function fakeNow() {
  return toFake(formatTime(new Date().toUTCString()));
}

function toFake(realTime) {
  const realDate = new Date(realTime);
  const fakeTime = new Date(realDate.getTime() - deltaMilliseconds);
  return fakeTime;
}

function toReal(fakeTime) {
  const fakeDate = new Date(fakeTime);
  const realTime = new Date(fakeDate.getTime() + deltaMilliseconds);
  return realTime;
}

function formatTime(time) {
  if (time.slice(-1) === "Z") {
    return time.slice(0, -1);
  }
  return time;
}

const fetchData = async (url) => {
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error("Error fetching data:", error);
    return { error };
  }
};

const getTimeline = async (userName, fakeTime, limit) => {
  const params = new URLSearchParams();

  userName ? params.append("user_name", userName) : null;
  fakeTime ? params.append("fake_time", formatTime(fakeTime)) : null;
  limit ? params.append("limit", limit) : null;

  const url = `${baseUrl}/timeline/?${params}`;

  const timeline = await fetchData(url);
  return timeline;
};

const getTweet = async (tweetId) => {
  const url = `${baseUrl}/tweet/${tweetId}/`;
  const tweet = await fetchData(url);
  return tweet;
};

const getOgImageUrl = (tweetId) => {
  return `${baseUrl}/tweet/${tweetId}/og.jpg`;
};

const getPosts = async (userName, fakeTime, limit) => {
  const params = new URLSearchParams();
  params.append("user_name", userName);

  fakeTime ? params.append("fake_time", formatTime(fakeTime)) : null;
  limit ? params.append("limit", limit) : null;

  const url = `${baseUrl}/posts/?${params}`;
  const posts = await fetchData(url);
  return posts;
};

const getProfile = async (userName) => {
  const url = `${baseUrl}/profile/${userName}/`;
  return await fetchData(url);
};

const getHashtag = async (hashtagText, fakeTime, limit) => {
  const params = new URLSearchParams();

  fakeTime ? params.append("fake_time", formatTime(fakeTime)) : null;
  limit ? params.append("limit", limit) : null;

  const url = `${baseUrl}/hashtag/${hashtagText}?${params}`;

  const hashtagTweets = await fetchData(url);
  return hashtagTweets;
};

const getTrending = async (fakeTime, limit) => {
  const params = new URLSearchParams();

  fakeTime ? params.append("fake_time", formatTime(fakeTime)) : null;
  limit ? params.append("limit", limit) : null;

  const url = `${baseUrl}/trending/?${params}`;

  const trendingHashtags = await fetchData(url);
  return trendingHashtags;
};

const searchTweets = async (query, fakeTime, limit) => {
  const params = new URLSearchParams();

  fakeTime ? params.append("fake_time", formatTime(fakeTime)) : null;
  limit ? params.append("limit", limit) : null;

  const url = `${baseUrl}/search/?${params}`;

  const body = {
    query: query || "",
  };

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Error fetching search results:", error);
    return { error };
  }
};

export {
  getTimeline,
  getTweet,
  getPosts,
  getProfile,
  getHashtag,
  getTrending,
  toFake,
  getOgImageUrl,
  fakeNow,
  formatTime,
  searchTweets,
};
