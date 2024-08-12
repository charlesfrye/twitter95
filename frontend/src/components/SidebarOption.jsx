"use client";

import { useRouter } from 'next/navigation';

function SidebarOption({ Icon, text, path }) {
  const router = useRouter();

  function handleClick() {
    router.push(path);
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
