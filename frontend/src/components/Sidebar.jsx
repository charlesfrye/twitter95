/* eslint-disable react/prop-types */
import SidebarOption from "./SidebarOption"; // Make sure the path is correct

function Sidebar({ options, className }) {
  function handleClick() {
    alert("Congrats! You just Tweeted!");
  }

  return (
    <div className={`sidebar ${className}`}>
      <img
        src="./public/logo.png"
        alt="Twitter Logo"
        className="logo-animate"
      />
      {options.map((option, index) => (
        <SidebarOption key={index} Icon={option.icon} text={option.text} />
      ))}
      <button onClick={handleClick}>Click me to Tweet!</button>
    </div>
  );
}

export default Sidebar;
