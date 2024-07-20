import "./App.css";
import { useEffect } from "react";
import { Outlet } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import StartupSound from "./components/StartupSound";
import { createGlobalStyle, ThemeProvider } from "styled-components";
import { styleReset } from "react95";
import original from "react95/dist/themes/original";
import ErrorBoundary from "./components/ErrorBoundary";
import MetaTags from "./components/MetaTags";

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
  const leftSidebarOptions = [
    { text: "Timeline", path: "/timeline" },
    { text: "About", path: "/" },
  ];

  const rightSidebarOptions = [];

  return (
    <ErrorBoundary>
      <MetaTags />
      <StartupSound />
      <ThemeProvider theme={original}>
        <GlobalStyles />
        <div className="app">
          <Sidebar className="sidebarLeft" options={leftSidebarOptions} />
          <div className="middle">
            <Outlet />
          </div>
          <Sidebar className="sidebarRight" options={rightSidebarOptions}>
            <div className="text-[#7FEE64] text-2xl">
              <a href="/">Twitter &apos;95</a>
              <br />
              <img
                src="/logo.png"
                alt="Twitter 95"
                className="logo-animate pt-4"
              />
              <a className="text-sm" href="https://modal.com">
                {" "}
                Powered by Modal
              </a>
            </div>
          </Sidebar>
        </div>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;
