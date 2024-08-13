"use client";

import { DatePicker__UNSTABLE } from "react95";
import { useState, useEffect, useContext } from "react";
import { fakeNow, formatTime } from "../services/database";
import { FakeTimeContext } from "./FakeTimeContext";
import { useRouter } from "next/navigation";
import "./TimeTravel.css";

function TimeTravel() {
  const router = useRouter();

  const { fakeTime, setFakeTime } = useContext(FakeTimeContext);
  // any url param will set the fakeTime in the browsing session
  const queryParams = new URLSearchParams(location.search);
  if (queryParams.get("fakeTime")) {
    setFakeTime(queryParams.get("fakeTime"));
  }

  const maxFakeTime = fakeNow();

  const startingDate = fakeTime
    ? fakeTime.split("T")[0]
    : maxFakeTime.toISOString().split("T")[0];
  let [date, setDate] = useState(startingDate);
  let [error, setError] = useState(null);

  useEffect(() => {
    if (fakeTime) {
      setDate(fakeTime.split("T")[0]);
    }
  }, [fakeTime]);

  function onAccept(date) {
    const attemptedFakeTime = new Date(date);
    if (attemptedFakeTime > maxFakeTime) {
      setError(
        "Sorry, the simulation has only run until " + maxFakeTime.toDateString()
      );

      // clear after a bit
      setTimeout(() => {
        setError(null);
      }, 5000);

      return;
    }

    const now = new Date();
    const hours = now.getUTCHours();
    const minutes = now.getUTCMinutes();
    const seconds = now.getUTCSeconds();

    const utcTime = `${hours.toString().padStart(2, "0")}:${minutes
      .toString()
      .padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`;

    let newFakeTime = new Date(`${date}T${utcTime}.000Z`);
    setFakeTime(formatTime(newFakeTime.toISOString()));
    router.push("/timeline");
  }

  return (
    <div className="banner align-middle mt-4">
      <DatePicker__UNSTABLE className="no-year" onAccept={onAccept} date={date}>
        {" "}
      </DatePicker__UNSTABLE>
      {error && (
        <p className="text-red-200 font-bold text-lg bg-red-500 p-1">{error}</p>
      )}
    </div>
  );
}

export default TimeTravel;
