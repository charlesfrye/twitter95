'use client';

import ErrorBoundary from "./ErrorBoundary";
import { ThemeProvider } from "styled-components";
import { FakeTimeProvider } from './FakeTimeContext';
import StartupSound from "./StartupSound";
import original from "react95/dist/themes/original";
import { useRouter, useSearchParams } from 'next/navigation';
import { useContext, useEffect } from "react";
import Sidebar from "./Sidebar";
import Trending from "./Trending";
import MetaTags from "./MetaTags";
import { FakeTimeContext } from './FakeTimeContext';
import { formatTime, fakeNow } from "../services/database";

function LayoutContent({ children }) {
  const router = useRouter();
  const { fakeTime, setFakeTime } = useContext(FakeTimeContext);

  const queryParams = useSearchParams();
  const render_as_og = queryParams.get("render_as_og");
  if (render_as_og) {
    // twitter renders 1600 px X 900 px, we'll halve that
    return (
      <ThemeProvider theme={original}>
        <div className="app" style={{ width: '800px', height: '450px' }}>
          {children}
        </div>
      </ThemeProvider>
    );
  }

  const leftSidebarOptions = [
    { text: "Timeline", path: "/timeline" },
    { text: "Search", path: "/search" },
    { text: "About", path: "/" },
  ];

  const rightSidebarOptions = [];

  const currentFakeTime = fakeNow();
  let displayTimeTravel = false;
  const hr = 60 * 60 * 1000;
  if (new Date(fakeTime) < currentFakeTime - hr) {
    displayTimeTravel = true;
  }

  function resetTimeTravel() {
    const newFakeTime = fakeNow();
    setFakeTime(newFakeTime.toISOString());
    router.push("/timeline");
  }

  useEffect(() => {
    const handleKeyDown = (event) => {
      if ((event.metaKey || event.ctrlKey) && event.key === "k") {
        event.preventDefault();
        router.push("/search");
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, []);

  return (
    <>
      <MetaTags />
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
          {children}
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
    </>
  );
}

export default function ClientLayout({ children }) {
  return (
    <ErrorBoundary>
      <FakeTimeProvider>
        <ThemeProvider theme={original}>
          <StartupSound />
          <LayoutContent>{children}</LayoutContent>
        </ThemeProvider>
      </FakeTimeProvider>
    </ErrorBoundary>
  );
}