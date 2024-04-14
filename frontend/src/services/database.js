// TODO: actually fetch posts data from the database

const fetchData = async () => {
  try {
    const inData = {
      user_id: "0",
      limit: 10,
    }
    const response = await fetch(
      "https://ex-twitter--database-fastapi-app.modal.run/timeline",
        {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json'
          },
          body: JSON.stringify(inData)
      }
      );
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Failed to fetch data:", error);
    throw error;
  }
};

const getFeed = async (limit, realTime, userId) => {
  // fetch limit tweets as of realTime (optionally for userId) from the db
  const response = await fetchData();
  return response;
};

const getTimeline = async (limit, realTime, userId) => {
  // fetch limit most recent tweets as of realTime (optionally for userId) from the db
  const response = await fetchData();
  return response;
};

const getPosts = async (limit, realTime, userId) => {
  // fetch limit most recent posts as of realTime for a given userId from the db (to put in profile page)
  const response = await fetchData();
  return response;
};

const getUser = async (userId) => {
  // fetch user data for a given userId from the db
  const response = await fetchData().user[userId];
  return response;
};

export { getFeed, getTimeline, getPosts, getUser };
