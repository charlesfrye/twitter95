const urlPrefix = "ex-twitter--db-client-api";
const urlSuffix =
  import.meta.env.VITE_DEV_BACKEND === "true" ? "-dev.modal.run" : ".modal.run";

const baseUrl = `https://${urlPrefix}${urlSuffix}`;

const deltaMilliseconds = 915235088 * 1000; // time from 1995 to 2024

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
  return time.slice(0, -1);
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

const getTimeline = async (userId, fakeTime, limit) => {
  const params = new URLSearchParams();

  userId ? params.append("user_id", userId) : null;
  fakeTime ? params.append("fake_time", formatTime(fakeTime)) : null;
  limit ? params.append("limit", limit) : null;

  const url = `${baseUrl}/timeline/?${params}`;

  const timeline = await fetchData(url);
  return timeline;
};

const getPosts = async (userId, fakeTime, limit) => {
  const params = new URLSearchParams();
  params.append("user_id", userId);

  fakeTime ? params.append("fake_time", formatTime(fakeTime)) : null;
  limit ? params.append("limit", limit) : null;

  const url = `${baseUrl}/posts/?${params}`;
  const posts = await fetchData(url);
  return posts;
};

const getProfile = async (userId) => {
  const url = `${baseUrl}/profile/${userId}/`;
  return await fetchData(url);
};

export { getTimeline, getPosts, getProfile, toFake };
