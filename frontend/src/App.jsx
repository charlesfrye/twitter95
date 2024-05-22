import "./App.css";
import { useEffect } from "react";
import { Outlet } from "react-router-dom";
import { useTheme } from "./components/ThemeContext";
import Sidebar from "./components/Sidebar";
import StartupSound from "./components/StartupSound";
import { FaHome, FaUserAlt, FaSearch } from "react-icons/fa";
import { createGlobalStyle, ThemeProvider } from "styled-components";
import { styleReset } from "react95";
import original from "react95/dist/themes/original";
import ErrorBoundary from "./components/ErrorBoundary";

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
    { icon: FaHome, text: "Home", path: "/timeline" },
    { icon: FaUserAlt, text: "Profile" },
  ];

  const rightSidebarOptions = [{ icon: FaSearch, text: "Search" }];

  useEffect(() => {
    document.body.className = theme;
  }, [theme]);

  return (
    <ErrorBoundary>
      <StartupSound />
      <ThemeProvider theme={original}>
        <GlobalStyles />
        <div className="app">
          <Sidebar className="sidebarLeft" options={leftSidebarOptions}>
            <div className="text-[#7FEE64]">
              <a href="https://modal.com">Powered by Modal</a>
            </div>
          </Sidebar>
          <Outlet />
          <Sidebar className="sidebarRight" options={rightSidebarOptions} />
        </div>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;
