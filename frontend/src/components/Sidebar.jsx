/* eslint-disable react/prop-types */
import SidebarOption from "./SidebarOption";

function Sidebar({ options, className, children }) {
  return (
    <div className={`sidebar ${className}`}>
      <img src="/logo.png" alt="Twitter 95" className="logo-animate" />
      {options.map((option, index) => (
        <SidebarOption
          key={index}
          Icon={option.icon}
          text={option.text}
          path={option.path}
        />
      ))}
      {children}
    </div>
  );
}

export default Sidebar;
