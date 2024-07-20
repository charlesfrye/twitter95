import { createContext, useContext, useState } from "react";

const ThemeContext = createContext("default");

export const useTheme = () => useContext(ThemeContext);

export const ThemeProvider = ({ children }) => {
  return (
    <ThemeContext.Provider value="default">{children}</ThemeContext.Provider>
  );
};
