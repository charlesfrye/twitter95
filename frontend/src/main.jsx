import React from "react";
import ReactDOM from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import { FakeTimeProvider } from "./components/FakeTimeContext";
import Profile from "./components/Profile.jsx";
import App from "./App.jsx";
import Feed from "./components/Feed.jsx";
import HashtagFeed from "./components/HashtagFeed.jsx";
import HomePage from "./components/HomePage.jsx";
import TweetPage from "./components/TweetPage.jsx";
import TimeTravel from "./components/TimeTravel.jsx";
import "./App.css";

const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    children: [
      {
        index: true,
        element: <HomePage />,
      },
      {
        path: "profile/:userId",
        element: <Profile />,
      },
      {
        path: "timeline",
        element: <Feed />,
      },
      { path: "time-travel", 
        element: <TimeTravel /> 
      },
      {
        path: "hashtag/:hashtagText",
        element: <HashtagFeed />,
      },
      {
        path: "tweet/:tweetId",
        element: <TweetPage />,
      }
    ],
  },
]);

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <FakeTimeProvider>
      <RouterProvider router={router} />
    </FakeTimeProvider>
  </React.StrictMode>
);
