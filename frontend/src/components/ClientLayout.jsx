"use client";
import { Suspense } from "react";
import ErrorBoundary from "./ErrorBoundary";
import { ThemeProvider } from "styled-components";
import { FakeTimeProvider } from "./FakeTimeContext";
import StartupSound from "./StartupSound";
import original from "react95/dist/themes/original";
import { useRouter, useSearchParams } from "next/navigation";
import { useContext, useEffect } from "react";
import Sidebar from "./Sidebar";
import Trending from "./Trending";
import MetaTags from "./MetaTags";
import { FakeTimeContext } from "./FakeTimeContext";
import { formatTime, fakeNow } from "../services/database";
import Marquee from "react-fast-marquee";

function LayoutContent({ children }) {
  const router = useRouter();
  const { fakeTime, setFakeTime } = useContext(FakeTimeContext);

  const queryParams = useSearchParams();

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
  }, [router]);

  const render_as_og = queryParams.get("render_as_og");
  if (render_as_og) {
    // twitter renders 1600 px X 900 px, we'll halve that
    return (
      <ThemeProvider theme={original}>
        <div className="flex justify-between items-stretch h-full min-h-full w-full" style={{ width: "800px", height: "450px" }}>
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

  
  return (
    <div className="h-full w-full ">
      <MetaTags />
      <div className="flex justify-between items-stretch h-full min-h-full w-full">
        <Sidebar className="z-10 h-100 fixed top-0 left-0 bottom-0" options={leftSidebarOptions} />
        <div className="w-full flex justify-center">
          <div className="w-3/5">
            <div className="h-6 mt-3">
              <Marquee className="w-10 text-[#7FEE64] hover:text-[#48ffa7]" gradient={true} gradientColor="black">
                  <a href="https://x.com/posts1995">&nbsp;Follow @Posts1995 on real twitter to keep up with the best from Twitter &apos;95.&nbsp;</a>
              </Marquee>
            </div>
            <div className="px-[10%]">
              {children}
            </div>
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
          </div>
        </div>
        <Sidebar className="z-10 h-100 fixed top-0 right-0 bottom-0" options={rightSidebarOptions}>
          <div className="text-[#7FEE64] text-2xl">
            <a href="/">Twitter &apos;95</a>
            <div className="flex justify-center mb-4">
              <img
                src="/logo.png"
                alt="Twitter 95"
                className="pt-4 animate-tilt w-1/6"
              />
            </div>
            <a className="text-sm" href="https://modal.com">
              {" "}
              #PoweredByModal
            </a>
          </div>
          <Trending />
        </Sidebar>
      </div>
    </div>
  );
}

export default function ClientLayout({ children }) {
  return (
    <ErrorBoundary>
      <FakeTimeProvider>
        <ThemeProvider theme={original}>
          <Suspense fallback={<div>Loading layout...</div>}>
            <LayoutContent>{children}</LayoutContent>
          </Suspense>
        </ThemeProvider>
      </FakeTimeProvider>
    </ErrorBoundary>
  );
}
