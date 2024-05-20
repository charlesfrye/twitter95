function SidebarOption({ Icon, text, path }) {
  return (
    <div className="sidebarOption">
      {Icon && <Icon />}
      <h2>
        <a href={path}>{text}</a>
      </h2>
    </div>
  );
}

export default SidebarOption;
