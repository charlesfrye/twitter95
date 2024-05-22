/* eslint-disable react/prop-types */
import SidebarOption from "./SidebarOption";

function Sidebar({ options, className, children }) {
  return (
    <div className={`sidebar ${className}`}>
      <div className="text-[#7FEE64]">
        <a href="/">Twitter &apos;95</a>
        <br />
        <a href="https://modal.com"> Powered by Modal</a>
      </div>
      <img src="/logo.png" alt="Twitter 95" className="logo-animate pt-4" />
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
