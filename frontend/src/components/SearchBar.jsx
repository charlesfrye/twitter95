"use client";

import { Button, TextInput } from "react95";
import { useEffect, useState } from "react";

function SearchBar({ onButtonClick }) {
  const placeholderOptions = [
    "Oklahoma City 4/21/95...",
    "Netscape...",
    "President Clinton...",
    "O.J. Simpson...",
    "Srebrenica 7/25/95...",
    "John Doe 2...",
    "Free Software...",
    "Windows 95...",
    "Timothy McVeigh...",
    "Rwanda...",
    "Newt Gingrich...",
    "Nuclear Disarmament...",
    "FuckMicrosoft...",
    "Aum Shinrikyo...",
    "SimulationTheory...",
    "Frederick Cuny...",
    "Scott O'Grady...",
    "Croatia...",
    "Al Gore...",
    "Bulls...",
    "Mickey Mantle...",
    "Stanley Cup...",
    "49ers win...",
    "Baseball strike...",
    "Pro-life...",
    "Pro-choice...",
    "Medicare...",
    "Balanced Budget...",
    "Terrorism...",
    "Nerve gas...",
    "Iraq WMD...",
    "Russia...",
    "War...",
  ];

  const [state, setState] = useState(() => {
    const initialPlaceholderIndex = Math.floor(
      Math.random() * placeholderOptions.length
    );
    return {
      value: "",
      placeholderIndex: initialPlaceholderIndex,
    };
  });
  useEffect(() => {
    const interval = setInterval(() => {
      setState((prevState) => {
        const randomOffset =
          Math.floor(Math.random() * (placeholderOptions.length - 1)) + 1;
        const newPlaceholderIndex =
          (prevState.placeholderIndex + randomOffset) %
          placeholderOptions.length;

        return {
          ...prevState,
          placeholderIndex: newPlaceholderIndex,
        };
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [placeholderOptions.length]);

  const handleChange = (e) => setState({ ...state, value: e.target.value });
  const go = () => {
    onButtonClick(state.value);
  };
  return (
    <div className="flex justify-center items-center">
      <div className="w-1/2">
        <TextInput
          value={state.value}
          placeholder={placeholderOptions[state.placeholderIndex]}
          onChange={handleChange}
          fullWidth
        />
      </div>
      <Button onClick={go}>Search</Button>
    </div>
  );
}

export default SearchBar;
