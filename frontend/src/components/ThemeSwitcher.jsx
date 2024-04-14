import { useTheme } from "./ThemeContext";

const ThemeSwitcher = () => {
  const { toggleTheme } = useTheme();

  return (
    <div>
      <button onClick={() => toggleTheme("default")}>Light</button>
      <button onClick={() => toggleTheme("dim")}>Dim</button>
      <button onClick={() => toggleTheme("dark")}>Dark</button>
      <button onClick={() => toggleTheme("space")}>Booyah</button>
    </div>
  );
};

export default ThemeSwitcher;
