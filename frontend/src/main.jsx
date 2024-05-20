import React from "react";
import ReactDOM from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import { ThemeProvider } from "./components/ThemeContext.jsx";
import Profile from "./components/Profile.jsx";
import App from "./App.jsx";
import Feed from "./components/Feed.jsx";
import HomePage from "./components/HomePage.jsx";
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
    ],
  },
]);

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <ThemeProvider>
      <RouterProvider router={router} />
    </ThemeProvider>
  </React.StrictMode>
);
