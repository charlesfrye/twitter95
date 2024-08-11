import { DatePicker__UNSTABLE } from "react95";
import { useState, useEffect, useContext } from "react";
import { fakeNow, formatTime } from "../services/database";
import { FakeTimeContext } from './FakeTimeContext';
import { useNavigate } from "react-router-dom";

function TimeTravel() {
  const navigate = useNavigate();

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

    // date is UTC like 1995-08-06
    // add 23hr, 59min, 59sec, 999ms to the end of the day
    let newFakeTime = new Date(`${date}T00:00:00.000Z`);
    newFakeTime.setUTCHours(23, 59, 59, 999);
    setFakeTime(formatTime(newFakeTime.toISOString()));
    navigate("/timeline");
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
