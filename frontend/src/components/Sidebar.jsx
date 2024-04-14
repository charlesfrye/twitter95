/* eslint-disable react/prop-types */
import SidebarOption from "./SidebarOption"; // Make sure the path is correct

function Sidebar({ options, className }) {
  return (
    <div className={`sidebar ${className}`}>
      <img src="../../public/logo.png" alt="Twitter Logo" />
      {options.map((option, index) => (
        <SidebarOption key={index} Icon={option.icon} text={option.text} />
      ))}
      <button>Click me to Tweet!</button>
    </div>
  );
}

export default Sidebar;
