/* eslint-disable react/prop-types */
import SidebarOption from "./SidebarOption"; // Make sure the path is correct

function Sidebar({ options }) {
  return (
    <div className="sidebar">
      <img src="../../public/logo.png" alt="Twitter Logo" />
      {options.map((option, index) => (
        <SidebarOption key={index} Icon={option.icon} text={option.text} />
      ))}
      <button className="tweetButton">Tweet</button>
    </div>
  );
}

export default Sidebar;
