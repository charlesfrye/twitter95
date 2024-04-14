import "./App.css";
import { useEffect } from "react";
import { useTheme } from "./components/ThemeContext";
import Feed from "./components/Feed";
import Sidebar from "./components/Sidebar";
import { FaHome, FaBell, FaUserAlt, FaCog, FaSearch } from "react-icons/fa";

function App() {
  const { theme } = useTheme();
  const leftSidebarOptions = [
    { icon: FaHome, text: "Home" },
    { icon: FaBell, text: "Notifications" },
    { icon: FaUserAlt, text: "Profile" },
  ];

  const rightSidebarOptions = [
    { icon: FaCog, text: "Settings" },
    { icon: FaSearch, text: "Search" },
  ];
  useEffect(() => {
    console.log(`Updating body class to ${theme}`);
    document.body.className = theme;
  }, [theme]);

  return (
    <div className="app">
      <Sidebar options={leftSidebarOptions} />
      <Feed />
      <Sidebar options={rightSidebarOptions} />
    </div>
  );
}

export default App;
