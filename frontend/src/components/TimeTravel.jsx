import { DatePicker__UNSTABLE } from "react95";
import { useState, useEffect } from "react";
import { toFake } from "../services/database";

function TimeTravel() {
  const queryParams = new URLSearchParams(location.search);
  let fakeTime = queryParams.get("fakeTime");
  const maxFakeTime = toFake(new Date());

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

    const newFakeTime = new Date(date);
    window.location.href = "/timeline?fakeTime=" + newFakeTime.toISOString();
  }

  return (
    <div className="banner align-middle mt-4">
      <DatePicker__UNSTABLE onAccept={onAccept} date={date}>
        {" "}
      </DatePicker__UNSTABLE>
      {error && (
        <p className="text-red-200 font-bold text-lg bg-red-500 p-1">{error}</p>
      )}
    </div>
  );
}

export default TimeTravel;
