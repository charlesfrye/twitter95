function SidebarOption({ Icon, text }) {
  return (
    <div className="sidebarOption">
      {Icon && <Icon />}
      <h2>{text}</h2>
    </div>
  );
}

export default SidebarOption;
