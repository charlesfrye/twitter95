import { createContext, useContext, useState } from "react";

const ThemeContext = createContext();

// eslint-disable-next-line react-refresh/only-export-components
export const useTheme = () => useContext(ThemeContext);

// eslint-disable-next-line react/prop-types
export const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState("default"); // default theme

  const toggleTheme = (themeName) => {
    setTheme(themeName);
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};
