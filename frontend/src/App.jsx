import "./App.css";
import { useEffect } from "react";
import { Route, Routes } from "react-router-dom";
import { useTheme } from "./components/ThemeContext";
import Feed from "./components/Feed";
import Profile from "./components/Profile";
import Sidebar from "./components/Sidebar";
import { FaHome, FaBell, FaUserAlt, FaCog, FaSearch } from "react-icons/fa";
import { createGlobalStyle, ThemeProvider } from "styled-components";
import { styleReset } from "react95";
import original from "react95/dist/themes/original";
import ErrorBoundary from "./components/ErrorBoundary";

// React95 fonts
import ms_sans_serif from "react95/dist/fonts/ms_sans_serif.woff2";
import ms_sans_serif_bold from "react95/dist/fonts/ms_sans_serif_bold.woff2";

const GlobalStyles = createGlobalStyle`
  ${styleReset}
  @font-face {
    font-family: 'ms_sans_serif';
    src: url('${ms_sans_serif}') format('woff2');
    font-weight: 400;
    font-style: normal;
  }
  @font-face {
    font-family: 'ms_sans_serif_bold';
    src: url('${ms_sans_serif_bold}') format('woff2');
    font-weight: bold;
    font-style: normal;
  }
  body, input, select, textarea {
    font-family: 'ms_sans_serif';
  }
`;

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
    <ErrorBoundary>
      <div className="app">
        <Sidebar className="sidebarLeft" options={leftSidebarOptions} />
        <ThemeProvider theme={original}>
          <GlobalStyles />
          <Routes>
            <Route path="/" element={<Feed />} />
            <Route path="/profile/:userId" element={<Profile />} />
          </Routes>
        </ThemeProvider>
        <Sidebar className="sidebarRight" options={rightSidebarOptions} />
      </div>
    </ErrorBoundary >
  );
}

export default App;
