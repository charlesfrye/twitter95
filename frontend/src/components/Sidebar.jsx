import "./Sidebar.css";
/* eslint-disable react/prop-types */
import SidebarOption from "./SidebarOption";

function Sidebar({ options, className, children}) {
  return (
    <div className={`sidebar ${className}`}>
      {children}
      {options.map((option, index) => (
        <SidebarOption
          key={index}
          Icon={option.icon}
          text={option.text}
          path={option.path}
        />
      ))}
    </div>
  );
}

export default Sidebar;
