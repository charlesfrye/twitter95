import "./App.css";
import { useEffect } from "react";
import { Route, Routes } from "react-router-dom";
import { useTheme } from "./components/ThemeContext";
import Feed from "./components/Feed";
import Profile from "./components/Profile";
import Sidebar from "./components/Sidebar";
import { FaHome, FaBell, FaUserAlt, FaCog, FaSearch } from "react-icons/fa";

function App() {
  const { theme } = useTheme();
  const leftSidebarOptions = [
    { icon: FaHome, text: "Home" },
    { icon: FaBell, text: "Notifs" },
    { icon: FaUserAlt, text: "Profile" },
  ];

  const rightSidebarOptions = [
    { icon: FaCog, text: "Settings" },
    { icon: FaSearch, text: "Search" },
  ];
  useEffect(() => {
    document.body.className = theme;
  }, [theme]);

  return (
    <div className="app">
      <Sidebar className="sidebarLeft" options={leftSidebarOptions} />
      <Routes>
        <Route path="/" element={<Feed />} />
        <Route path="/profile/:userId" element={<Profile />} />
      </Routes>
      <Sidebar className="sidebarRight" options={rightSidebarOptions} />
    </div>
  );
}

export default App;
