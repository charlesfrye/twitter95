import "./App.css";
import { Outlet } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import StartupSound from "./components/StartupSound";
import { createGlobalStyle, ThemeProvider } from "styled-components";
import { styleReset } from "react95";
import original from "react95/dist/themes/original";
import ErrorBoundary from "./components/ErrorBoundary";
import Trending from "./components/Trending";
import MetaTags from "./components/MetaTags";
import { FakeTimeContext } from "./components/FakeTimeContext";
import { useContext, useEffect } from "react";
import { useNavigate } from "react-router-dom";

import ms_sans_serif from "react95/dist/fonts/ms_sans_serif.woff2";
import ms_sans_serif_bold from "react95/dist/fonts/ms_sans_serif_bold.woff2";
import { formatTime, fakeNow } from "./services/database";

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
  const navigate = useNavigate();

  const leftSidebarOptions = [
    { text: "Timeline", path: "/timeline" },
    { text: "Time Travel", path: "/time-travel" },
    { text: "About", path: "/" },
  ];

  const rightSidebarOptions = [];

  // we hack in a query param to render images in fixed dimensions for use by url screenshotting api as a pseudo og image
  const queryParams = new URLSearchParams(location.search);
  const render_as_og = queryParams.get("render_as_og");
  if (render_as_og) {
    // twitter renders 1600 px X 900 px, we'l halve that
    return (
      <ThemeProvider theme={original}>
        <GlobalStyles />
        <div className="app">
          <Outlet />
        </div>
      </ThemeProvider>
    );
  }

  const { fakeTime, setFakeTime } = useContext(FakeTimeContext);
  const currentFakeTime = fakeNow();
  let displayTimeTravel = false;
  const hr = 60 * 60 * 1000;
  if (new Date(fakeTime) < currentFakeTime - hr) {
    displayTimeTravel = true;
  }

  function resetTimeTravel() {
    const newFakeTime = fakeNow();
    setFakeTime(newFakeTime.toISOString());
    navigate("/timeline");
  }

  // cmd+k to go to time travel
  useEffect(() => {
    const handleKeyDown = (event) => {
      if ((event.metaKey || event.ctrlKey) && event.key === "k") {
        navigate("/time-travel");
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, []);

  return (
    <ErrorBoundary>
      <MetaTags />
      <StartupSound />
      <ThemeProvider theme={original}>
        <GlobalStyles />
        <div className="app">
          <Sidebar className="sidebarLeft" options={leftSidebarOptions} />
          <div className="middle">
            {displayTimeTravel && (
              <div className="fixed bottom-0 left-0 w-full z-50">
                <p className="bg-[#7FEE64] py-1 text-black ">
                  Currently viewing from{" "}
                  {new Date(formatTime(fakeTime)).toDateString()},
                  <a
                    className="underline cursor-pointer hover:text-gray-500 ml-1"
                    onClick={resetTimeTravel}
                  >
                    click here to reset
                  </a>
                </p>
              </div>
            )}
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
                #PoweredByModal
              </a>
            </div>
            <Trending />
          </Sidebar>
        </div>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;
