import "./App.css";
import { useEffect } from "react";
import { useTheme } from "./components/ThemeContext";
import { BrowserRouter as Router, Route, Link } from "react-router-dom";
import Feed from "./components/Feed";
// import Profile from "./components/Profile";

function App() {
  const { theme } = useTheme();

  useEffect(() => {
    console.log(`Updating body class to ${theme}`);
    document.body.className = theme;
  }, [theme]);

  return (
    <div className="app">
      <header className="nav">
        <Link to="/feed">Feed </Link>
        <Link to="/profile">Profile</Link>
      </header>
      <div className="main-content">
        <div className="sidebar left-sidebar"></div>
        <div className="content">
          <Router>
            <Route path="/feed" component={Feed} />
          </Router>
        </div>
        <div className="sidebar right-sidebar"></div>
      </div>
    </div>
  );
}

export default App;
