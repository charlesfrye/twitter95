import { useNavigate } from "react-router-dom";

function SidebarOption({ Icon, text, path }) {
  const navigate = useNavigate();

  function handleClick() {
    navigate(path);
  }

  return (
    <div className="sidebarOption">
      {Icon && <Icon />}
      <h2>
        <a onClick={handleClick}>{text}</a>
      </h2>
    </div>
  );
}

export default SidebarOption;
